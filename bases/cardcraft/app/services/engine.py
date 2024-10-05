import asyncio
import functools
import logging
import multiprocessing
import os
import time
import signal
import sys
import time
import typing as T

from multiprocessing.synchronize import Lock as LockT
from types import SimpleNamespace

from cardcraft.app.services.db import gamedb
from cardcraft.app.services.game import Event, Match, Target
from cardcraft.app.services.mem import mem
from cardcraft.app.services.nemesis import Nemesis


class Engine:

    # turn events to
    resolutions: list[T.Callable] = []

    async def card(self, query: dict):
        """find card info

        @note this method exists to separate DB querying from the game engine
        @note WARNING: NEVER try to do DB inserts from within the game engine
        """
        return await gamedb.cards.find_one(query)

    async def parse(self, match: Match, event: Event):
        """parses free-text event and performs match state updates

        @since ?
        """
        entity, entry, *_ = event

        # detect and process card movement
        # (like "$me plays card 123 to field position XYZ")
        card_play_patt = r"\$(?P<player>\w+) plays card (?P<card>\w+) to field position (?P<position>\w+)"
        card_play = re.match(card_play_patt, entry)
        if card_play is not None:

            cid: str = card_play.group("card")
            card: dict = await self.card({"id": cid})

            _, *t = card_play.group("position")

            # def resolution(match: Match):
            if target_type == "field":
                if cid not in match.players[entity]["hand"]:
                    logging.warning(f"{entity} tried to play a card not in hand")
                    return False

                match.players[entity]["hand"].pop(
                    match.players[entity]["hand"].index(cid)
                )
                *path, tail = map(int, t)

                functools.reduce(lambda a, e: a[e], path, match.fields)[tail] = card  # type: ignore[arg-type, return-value, call-overload]

            # self.resolutions.append(resolution)

        # detect and register attacks
        # (like "player uses 8c3c71cdfb1ebe8d14d00c49d4f11051 to attack unit-bot1")
        attack_patt = r"(?P<player>\w+) uses (?P<card>\w+) to attack (?P<unit>\w+)"
        atrack = re.match(attack_patt, entry)
        if attack is not None:
            opponent: str = attack.group("unit")  # type: ignore[no-redef]
            cid: str = attack.group("card")  # type: ignore[no-redef]
            atk: int = int((await self.card({"id": cid})).get("E_value"))

            def resolution(match: Match):
                if opponent in match.players:
                    # attacks the opponent directly
                    match.players[opponent]["hp"] -= atk

            self.resolutions.append(resolution)

        # detect possible responses
        # ...

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

                match.cursor[1] += 1
                continue

            if hasattr(match, f"_can_{fn}") and not getattr(match, f"_can_{fn}"):
                logging.warning(f"failed attempt to {fn}")
                match.cursor[1] += 1
                continue

            if args is not None:
                args = map(str.strip, str(args).split(","))

            if args is not None:
                getattr(match, fn)(entity, *args)
            else:
                getattr(match, fn)(entity)

            match.cursor[1] = 0 if fn == "end_turn" else match.cursor[1] + 1

        # resolve the turn events
        if (
            0 < len(match.turns[turn_idx])
            and match.turns[turn_idx][-1][1] == "end_turn"
        ):
            match.cursor[0] += 1
            match.cursor[1] = 0
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


engines: dict[str, Engine] = {}


def loop(lock: LockT):
    """the game loop

    @since ?

    @todo refer some things from memory to prevent object instantation
          and release on every single iteration
    """

    async def game():
        run: bool = True

        def stop(*a):
            run = False
            sys.exit()

        signal.signal(signal.SIGINT, stop)
        refresh: float = 0.6

        with lock:
            while run:
                async for match in gamedb.matches.find(
                    {"finished": None, "winner": None}
                ):
                    state = Match.create(match)

                    if match["id"] not in engines:
                        engines[match["id"]] = Engine()

                    changed = await engines[match["id"]].process(state)

                    if changed:
                        state = changed

                    if state.winner is None:
                        opkey: T.Optional[str] = next(
                            filter(
                                lambda e: e is not None and e.startswith("bot"),
                                state.players.keys(),
                            ),
                            None,
                        )
                        if opkey is not None and state.get(
                            "is_turn", Target.Player, opkey
                        ):
                            Nemesis(opkey).do(match=state)

                    then = state._asdict()

                    if changed:
                        await gamedb.matches.replace_one({"id": then["id"]}, then)

                    await asyncio.sleep(refresh)

                time.sleep(refresh)

    asyncio.run(game())
