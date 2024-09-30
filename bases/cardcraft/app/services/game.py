import functools
import logging
import random
import time
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

    # match winner
    winner: T.Optional[str] = None

    # reserved events for future turns
    futures: dict[list[Event]] = {}

    # player data
    players: dict[str, dict] = {}

    # player response options
    responses: dict[str, dict] = {}

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

    def end(self) -> 'Match':
        if any(filter(lambda e: e["hp"] <= 0, self.players.values())):
            winner: T.Optional[str] = None
            for k, v in self.players.items():
                if v["hp"] > 0:
                    winner = k
                    break

            assert winner is not None
            
            return self._replace(winner=winner, finished=int(time.time()))

    def end_turn(self, player: str):
        self.turns.append([])

    def _can_draw(self, ttype: Target, t: T.Any) -> bool:
        if ttype == Target.Player:
            drawn = any(filter(lambda e: e[0] == t and e[1] == "draw", self.turns[-1]))
            if drawn:
                return False

            return self._is_turn(ttype, t)

        return False

    def _can_play(self, ttype: Target, t: T.Any) -> bool:
        return self._is_turn(ttype, t)

    def _can_respond(self, ttype: Target, t: T.Any) -> bool:
        return self.responses.get(t, None) is not None

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

        @param op_perc float
        @param op_dmg_key str
        @param pl_perc float
        @param pl_dmg_key str

        @since 2024-09-22
        """

        card: dict = {}
        target: str = next(
            filter(lambda e: e != played_by, self.data["players"].keys()), None
        )
        dmg = int(card[op_dmg_key])

        self.do(target, "life", (-1 * (op_perc * int(card[op_dmg_key]))))
        self.do(played_by, "life", (-1 * (pl_perc * int(card[pl_dmg_key]))))

    def v1_debuff(self, card_id: str, played_by: str, stat: T.Literal["atk", "def"], amt: int):
        """card can debuff targeted enemy card for $AMT of $STAT

        @param stat ark|def
        @param amt int

        @since ?
        """
        pass

    def v1_debuff_attacking(self, card_id: str, played_by: str, stat: T.Literal["atk", "def"], amt: int):
        """card can debuff targeted attacking enemy card for $AMT of $STAT

        @param stat atk|def
        @param amt int

        @since ?
        """
        pass