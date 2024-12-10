import functools
import logging
import operator
import typing as T

from abc import abstractmethod
from pyrsistent import PVector, freeze, thaw, v

from cardcraft.game.db import gamedb
from cardcraft.game.system import Match, Event


class Engine(T.Protocol):
    @abstractmethod
    async def parse(self, match: Match, event: Event) -> Match:
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

    async def process(self, match: Match) -> Match:
        """executes turn events, makes game state changes

        @since 27-09-2024.
        """
        changed: Match = match

        turn_idx, event_idx = match.cursor
        if turn_idx >= len(match.turns):
            print("no turns!")
            return match

        for event in match.turns[turn_idx][event_idx:]:
            entity, fn, args = event

            if not hasattr(match, fn):
                # try to parse
                changed = await self.parse(changed, event)
                changed = changed.set(
                    "cursor", match.cursor.set(1, match.cursor[1] + 1)
                )

                continue

            if hasattr(match, f"_can_{fn}") and not getattr(match, f"_can_{fn}"):
                logging.warning(f"failed attempt to {fn}")

                changed = match.set("cursor", match.cursor.set(1, match.cursor[1] + 1))
                continue

            if args is not None:
                args = map(str.strip, str(args).split(","))

            if args is not None:
                changed = getattr(match, fn)(entity, *args)
            else:
                changed = getattr(match, fn)(entity)

            changed = changed.set(
                "cursor",
                match.cursor.set(1, 0 if fn == "end_turn" else match.cursor[1] + 1),
            )

        # resolve the turn events
        if (
            0 < len(changed.turns[turn_idx])
            and changed.turns[turn_idx][-1][1] == "end_turn"
        ):
            changed = changed.set("cursor", changed.cursor.set(0, match.cursor[0] + 1))
            changed = changed.set("cursor", changed.cursor.set(1, 0))
            changed = self.resolve(changed)
            self.resolutions = []

            # end if conditions are met
            done = changed.end()
            if done is not None:
                return done

            return changed

        # nothing has happened
        if event_idx == changed.cursor[1]:
            return match

        return changed

    def resolve(self, match: Match) -> Match:
        """resolves a single turn, updates match state

        @since ?
        """
        changed = match
        for fn in reversed(self.resolutions):
            changed = fn(changed)

        return changed


class DemoEngine(BaseEngine):
    async def parse(self, match: Match, event: Event) -> Match:
        """parses free-text event and performs match state updates

        @since ?
        """
        entity, line, *_ = event
        entry = line.split(" ")

        # parsers

        var = lambda e, vname: e

        # fmt: off
        # "$me plays card 123 to field position XYZ"

        # "player returns card 123 to hand"

        # "player uses 8c3c71cdfb1ebe8d14d00c49d4f11051 to attack unit-bot1"
        # fmt: on

        # detect and process card movement
        if "plays card" in line and "position " in line:
            # fmt: off
            card_id = entry[entry.index("card")+1]
            target_id = entry[entry.index("position")+1]
            # fmt: on

            card: dict = await self.card({"id": card_id})

            # def resolution(match: Match):
            if card_id not in match.players.get(entity).get("hand"):
                logging.warning(f"{entity} tried to play a card not in hand")
                return False

            hand = match.players[entity]["hand"].pop(
                match.players[entity]["hand"].index(card_id)
            )
            player = match.players[entity].set("hand", hand)
            players = match.players.set(entity, player)

            changed = match.set("players", players)

            *path, tail = map(int, filter(str.isnumeric, target_id))

            fields = thaw(changed.fields)
            functools.reduce(lambda a, e: a[e], path, fields)[tail] = {
                "id": card_id
            }  # ... card  # type: ignore[arg-type, return-value, call-overload]

            return changed.set("fields", freeze(fields))
            # self.resolutions.append(resolution)

        # card-to-field attack
        if " uses card " in line and " to attack f-" in line:
            # take out cards, compare them, and resolve attack results
            target_position = entry[entry.index("attack") + 1]
            card_id = entry[entry.index("card") + 1]

            card = await self.card({"id": card_id})
            fullpath = list(map(int, filter(str.isnumeric, target_position)))
            *path, tail = fullpath

            scoped = match.fields
            for e in fullpath:
                scoped = scoped[e]

            target = scoped

            a, b = list(map(operator.itemgetter("E_value"), [card, target]))
            if a < b:
                newpath = []

                # find path to card a to destroy card a
                for i, _ in enumerate(match.fields):
                    for j, _ in enumerate(match.fields[i]):
                        if match.fields[i][j] is None:
                            continue

                        if match.fields[i][j]["id"] == card_id:
                            path = [i]
                            tail = j

                            newpath = path + [tail]
                            break

                assert newpath, "Card not in field"

            fields = thaw(match.fields)
            functools.reduce(lambda a, e: a[e], path, fields)[tail] = None
            return match.set("fields", freeze(fields))

        # detect and register attacks
        if " uses card " in line and " to attack " in line:
            card_id = entry[entry.index("card") + 1]
            target_id = entry[entry.index("attack") + 1]

            card = await self.card({"id": card_id})

            atk: int = int(card.get("E_value"))

            def resolution(match: Match) -> Match:
                if target_id in match.players:
                    # attacks the opponent directly
                    player = match.players[target_id].set(
                        "hp", match.players[target_id].hp - atk
                    )
                    players = match.players.set(target_id, player)
                    return match.set("players", players)

            self.resolutions.append(resolution)
            return match

        # detect possible responses
        # ...
        return match
