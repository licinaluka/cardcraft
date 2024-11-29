import functools
import logging
import random
import time
import typing as T

from bson import ObjectId
from enum import Enum
from pyrsistent import PMap, PVector, m, v, freeze, thaw

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
    fields: PVector[PVector[T.Optional[dict]]]

    # player with first turn
    opener: str

    # when the match was created
    created: T.Optional[int]

    # when the match was finished
    finished: T.Optional[int]

    # match winner
    winner: T.Optional[str] = None

    # reserved events for future turns
    futures: dict[str, list[Event]] = {}

    # player data
    players: PMap[str, PMap] = m()

    # player response options
    responses: PMap[str, PVector[str]] = m()

    # turn and event evaluated at the moment
    cursor: PVector[int] = v(0, 0)

    # list of turns and events in each turn
    turns: PVector[PVector[Event]] = v(v())

    @staticmethod
    def create(data: dict):
        data.pop("_id")
        return Match(**freeze(data))

    def asdict(self) -> dict:
        return thaw(self)

    def do(self, e: str, a: str, val: T.Any) -> None:
        self.turns[-1].append(Event(e, a, val))

    def get(self, fn: str, ttype: Target, t: T.Any) -> T.Union[bool, int]:
        method = f"_{fn}"

        if not hasattr(self, method):
            raise Exception(f"Match cannot get {fn}")

        return getattr(self, method)(ttype, t)

    def end(self) -> T.Optional["Match"]:
        def was_defeated(e: dict) -> bool:
            return e["hp"] <= 0

        defeated: T.Iterable[dict] = filter(was_defeated, self.players.values())
        if not any(defeated):
            return None

        winner: T.Optional[str] = None
        for k, v in self.players.items():
            if v["hp"] > 0:
                winner = k
                break

        assert winner is not None

        return self._replace(winner=winner, finished=int(time.time()))

    def end_turn(self, player: str):
        self.turns.append(v())

    def _can_draw(self, ttype: Target, t: T.Any) -> bool:
        if ttype == Target.Player:

            def had_drawn(e: Event) -> bool:
                return e[0] == t and e[1] == "draw"

            drawn = any(filter(had_drawn, self.turns[-1]))  # type: ignore[arg-type]
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

            card_id = self.players[player]["deck"]["cards"].delete(-1)
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
        target: T.Optional[str] = next(
            filter(lambda e: e != played_by, self.players.keys()), None
        )
        dmg = int(card[op_dmg_key])

        if target is None:
            return None

        self.do(target, "life", (-1 * (op_perc * int(card[op_dmg_key]))))
        self.do(played_by, "life", (-1 * (pl_perc * int(card[pl_dmg_key]))))

    def v1_debuff(
        self, card_id: str, played_by: str, stat: T.Literal["atk", "def"], amt: int
    ):
        """card can debuff targeted enemy card for $AMT of $STAT

        @param stat ark|def
        @param amt int

        @since ?
        """
        pass

    def v1_debuff_attacking(
        self, card_id: str, played_by: str, stat: T.Literal["atk", "def"], amt: int
    ):
        """card can debuff targeted attacking enemy card for $AMT of $STAT

        @param stat atk|def
        @param amt int

        @since ?
        """
        pass
