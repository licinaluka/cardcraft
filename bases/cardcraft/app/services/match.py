import asyncio
import functools
import logging
import random
import time
import typing as T

from bson import ObjectId
from enum import Enum
from cardcraft.app.services.db import gamedb
from cardcraft.app.services.mem import mem


def loop():
    async def game():
        while True:
            async for match in gamedb.matches.find({}):
                state = Match.create(match)
                state.move()
                then = state._asdict()
                await gamedb.matches.replace_one({"id": then["id"]}, then)
                time.sleep(5)

    asyncio.run(game())


class Event(T.NamedTuple):
    e: str
    a: str
    v: T.Any


class Target(Enum):
    Player = 1
    Field = 2


class Match(T.NamedTuple):

    # identifier
    id: str

    # play area(s)
    fields: list[list[T.Optional[str]]]

    # player with first turn
    opener: str

    # when the match was finished
    finished: T.Optional[str]

    # reserved events for future turns
    futures: dict[list[Event]] = {}

    # player data
    players: dict[str, dict] = {}

    # turn and event evaluated at the moment
    cursor: list[int] = [0, 0]

    # list of turns and events in each turn
    turns: list[list[Event]] = [[]]

    @staticmethod
    def create(data: dict):
        data.pop("_id")
        return Match(**data)

    def do(self, e: str, a: str, v: T.Any):
        self.turns[-1].append(Event(e, a, v))

    def get(self, fn: str, ttype: Target, t: T.Any) -> T.Union[bool, int]:
        method = f"_{fn}"

        if not hasattr(self, method):
            raise Exception(f"Match cannot get {fn}")

        return getattr(self, method)(ttype, t)

    def move(self) -> bool:
        turn_idx, event_idx = self.cursor
        if turn_idx >= len(self.turns):
            return False

        for event in self.turns[turn_idx][event_idx:]:
            entity, fn, args = event

            if not hasattr(self, fn):
                logging.warning(f"not implemented - {fn}")
                del self.turns[turn_idx][event_idx]
                continue

            if hasattr(self, f"_can_{fn}") and not getattr(self, f"_can_{fn}"):
                logging.warning(f"failed attempt to {fn}")
                del self.turns[turn_idx][event_idx]
                continue

            print({"EXEC": [fn, entity, args]})
            if args is not None:
                args = map(str.strip, str(args).split(","))

            if args is not None:
                getattr(self, fn)(entity, *args)
            else:
                getattr(self, fn)(entity)

            self.cursor[1] = 0 if fn == "end_turn" else event_idx + 1

        return True

    def end_turn(self, player: str):
        self.cursor[0] += 1
        self.cursor[1] = 0
        self.turns.append([])

    def _can_draw(self, ttype: Target, t: T.Any) -> bool:
        if ttype == Target.Player:
            drawn = any(filter(lambda e: e[0] == t and e[1] == "draw", self.turns[-1]))
            if drawn:
                return False

            return self._is_turn(ttype, t)

        return False

    def _can_play(self, ttype: Target, t: T.Any) -> bool:
        return False

    def _is_turn(self, ttype: Target, t: T.Any) -> bool:
        if ttype == Target.Player:
            turn, _ = self.cursor
            return turn % 2 == (0 if self.opener == t else 1)

        return False

    def draw(self, player: str, num: str):
        n = int(num)
        while n > 0:
            n -= 1
            if 1 > len(self.players[player]["deck"]["cards"]):
                break

            card_id = self.players[player]["deck"]["cards"].pop()
            self.players[player]["hand"].append(card_id)

    def play(self, player: str, _from: str, _to: str):
        origin, card_id = _from.split("-")
        target, *_to = _to.split("-")

        hand_to_field = origin == "h" and target == "f"

        if hand_to_field:
            self.players[player]["hand"].pop(
                self.players[player]["hand"].index(card_id)
            )

            *path, tail = map(int, _to)
            functools.reduce(lambda a, e: a[e], path, self.fields)[tail] = card_id

    def v1_barrage(
        self,
        card_id: str,
        played_by: str,
        op_perc: float,
        op_dmg_key: str,
        pl_perc: float,
        pl_dmg_key: str,
    ):
        """card can damage the opponent for N% and player for N% of card's stat

        @since 2024-09-22
        """

        card: dict = {}
        target: str = next(
            filter(lambda e: e != played_by, self.data["players"].keys()), None
        )
        dmg = int(card[op_dmg_key])

        self.do(target, "life", (-1 * (op_perc * int(card[op_dmg_key]))))
        self.do(played_by, "life", (-1 * (pl_perc * int(card[pl_dmg_key]))))


class Nemesis:
    name: str

    def __init__(self, name: str):
        self.name = name

    def do(self, match: Match) -> bool:
        """do something"""

        if not match.get("is_turn", Target.Player, self.name):
            logging.warning("not my turn...")
            return False

        options: list = []
        for action, args in {
            "draw": "3",
            # "play": random.choice(match.players[self.name]["hand"]),
        }.items():
            if match.get(f"can_{action}", Target.Player, self.name):
                options.append([self.name, action, args])

        # time.sleep(random.randint(1, 3))
        if 0 < len(options):
            match.do(*random.choice(options))

            # end turn
            match.do(self.name, "end_turn", None)
            return True

        # skip turn
        match.do(self.name, "end_turn", None)
        return False
