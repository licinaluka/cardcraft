import functools
import logging
import random
import typing as T

from bson import ObjectId
from enum import Enum
from cardcraft.app.services.mem import mem



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

    # when the match was created
    created: T.Optional[int]

    # when the match was finished
    finished: T.Optional[int]

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
            print(f"DRAWING {n} CARDS")
            n -= 1
            if 1 > len(self.players[player]["deck"]["cards"]):
                break

            card_id = self.players[player]["deck"]["cards"].pop()
            self.players[player]["hand"].append(card_id)

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


