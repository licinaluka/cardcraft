import logging
import typing as T

from abc import abstractmethod
from pyrsistent import PVector, v

from cardcraft.game.db import gamedb
from cardcraft.game.system import Match, Event


class Engine(T.Protocol):
    @abstractmethod
    async def parse(self, match: Match, event: Event):
        """?"""


class BaseEngine(Engine):

    # turn events to
    resolutions: list[T.Callable] = []

    async def card(self, query: dict):
        """find card info

        @note this method exists to separate DB querying from the game engine
        @note WARNING: NEVER try to do DB inserts from within the game engine
        """
        return await gamedb.cards.find_one(query)

    async def process(self, match: Match) -> T.Optional[Match]:
        """executes turn events, makes game state changes

        @since 27-09-2024.
        """

        turn_idx, event_idx = match.cursor
        if turn_idx >= len(match.turns):
            print("no turns!")
            return None

        for event in match.turns[turn_idx][event_idx:]:
            entity, fn, args = event

            if not hasattr(match, fn):
                # try to parse
                await self.parse(match, event)
                match.cursor.set(1, match.cursor[1] + 1)
                continue

            if hasattr(match, f"_can_{fn}") and not getattr(match, f"_can_{fn}"):
                logging.warning(f"failed attempt to {fn}")

                match.cursor.set(1, match.cursor[1] + 1)
                continue

            if args is not None:
                args = map(str.strip, str(args).split(","))

            if args is not None:
                getattr(match, fn)(entity, *args)
            else:
                getattr(match, fn)(entity)

            match.cursor.set(1, 0 if fn == "end_turn" else match.cursor[1] + 1)

        # resolve the turn events
        if (
            0 < len(match.turns[turn_idx])
            and match.turns[turn_idx][-1][1] == "end_turn"
        ):
            match.cursor.set(0, match.cursor[0] + 1)
            match.cursor.set(1, 0)
            self.resolve(match)
            self.resolutions = []

            # end if conditions are met
            done = match.end()
            if done is not None:
                return done

            return match

        # nothing has happened
        if event_idx == match.cursor[1]:
            return None

        return match

    def resolve(self, match: Match) -> None:
        """resolves a single turn, updates match state

        @since ?
        """
        for fn in reversed(self.resolutions):
            fn(match)
