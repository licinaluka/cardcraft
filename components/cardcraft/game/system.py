import functools
import logging
import random
import time
import typing as T

from bson import ObjectId
from enum import Enum
from pyrsistent import PClass, PMap, PVector, field, m, v, freeze, thaw


Stat = T.Union[str, int, float, bool, None]
Mapping = T.Tuple[str, Stat]

DefaultCardMapping: dict = {
    "name": "A_value",
    "type": "B_value",
    "class": "C_value",
    "atk": "E_value",
    "def": "F_value",
}


class Card(PClass):
    """a class that can be instantiated with card data and a user configured
       mapping between a generic stat (atk, def, type, class, archety, cost, etc)
       and any random card field and optionally a default value if none set

    @note this lets a end user define any card layout they want and a mapping
          for the actual game engine to use
    """

    data: PMap[str, Stat] = field(PMap)
    mapping: PMap[str, Mapping] = field(PMap)

    def get(self, stat: str) -> Stat:
        mapping: T.Optional[Mapping] = self.mapping.get(stat)

        if mapping is None:
            priv = f"_{stat}"
            if priv in self.data:
                mapping = priv, None

        if mapping is None:
            return None

        key, default = mapping

        return self.data.get(key, None)

    def rotate(self, degrees: int) -> "Card":
        if self.data.get("_rotation_locked"):
            raise AssertionError
 
        old: int = self.data.get("_rotation", 0)

        self.data.set("_rotation", old + degrees)
        return self


class Event(T.NamedTuple):
    e: str
    a: str
    v: T.Any


class PlayerPot:
    txsig: T.Optional[str]
    lamports: int = 0


class Player(PClass):
    pot: PlayerPot
    hp: int = field(int)
    hpmax: int
    name: str = field(str)
    deck: PMap = field(PMap)
    hand: PVector = field(PVector)


class Target(Enum):
    Player = 1
    Field = 2


class Match(PClass):

    # identifier
    id: str = field(str)

    # play area(s)
    fields: PVector[PVector[T.Optional[dict]]] = field(PVector)

    # player with first turn
    opener: str = field(str)

    # when the match was created
    created: T.Optional[int] = field(int)

    # who has the first move
    opener: T.Optional[str] = field([str, type(None)])

    # when the match was finished
    finished: T.Optional[int] = field([int, type(None)])

    # match winner
    winner: T.Optional[str] = field([str, type(None)])

    # reserved events for future turns
    futures: PMap[str, PVector[Event]] = field(PMap)

    # player data
    players: PMap[str, PMap] = field(PMap)

    # player response options
    responses: PMap[str, PVector[str]] = field(PMap)

    # turn and event evaluated at the moment
    cursor: PVector[int] = field(PVector)

    # list of turns and events in each turn
    turns: PVector[PVector[Event]] = field(PVector)

    @staticmethod
    def fromdict(data: dict) -> "Match":
        data.pop("_id", None)
        return Match(**freeze(data))

    def do(self, e: str, a: str, val: T.Any) -> "Match":
        registered: PVector[Event] = self.turns[-1].append(Event(e, a, val))
        return self.set("turns", self.turns.set(-1, registered))

    def get(self, fn: str, ttype: Target, t: T.Any) -> T.Union[bool, int]:
        method = f"_{fn}"

        if not hasattr(self, method):
            raise Exception(f"Match cannot get {fn}")

        return getattr(self, method)(ttype, t)

    def end(self) -> "Match":
        def was_defeated(e: dict) -> bool:
            return e.hp <= 0

        defeated: T.Iterable[dict] = filter(was_defeated, self.players.values())
        if not any(defeated):
            return self

        winner: T.Optional[str] = None
        for k in self.players.keys():
            if self.players[k].hp > 0:
                winner = k
                break

        if winner is None:
            raise AssertionError

        return self.set("winner", winner).set("finished", int(time.time()))

    def end_turn(self, player: str):
        return self.set("turns", self.turns.append(v()))

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

    def draw(self, player: str, num: str) -> "Match":
        # draw cards to hand
        hand = v()

        n = int(num)
        while n > 0:
            n -= 1
            if 1 > len(self.players[player].deck["cards"]):
                break

            card_id = self.players[player].deck["cards"].delete(-1)
            hand = self.players[player].hand.append(card_id)

        # set hand to player
        changed = self.players[player].set("hand", hand)

        # set player to players
        players = self.players.set(player, changed)

        # set players to match
        return self.set("players", players)

    def v1_barrage(
        self,
        card_id: str,
        played_by: str,
        op_perc: float,
        op_dmg_key: str,
        pl_perc: float,
        pl_dmg_key: str,
    ) -> "Match":
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

        return self.do(target, "life", (-1 * (op_perc * int(card[op_dmg_key])))).do(
            played_by, "life", (-1 * (pl_perc * int(card[pl_dmg_key])))
        )

    def v1_buff(
        self, card_id: str, played_by: str, stat: T.Literal["atk", "def"], amt: int
    ):
        """?

        @since ?
        @todo target something
        """
        direction = "increasing" if amt > 0 else "decreasing"
        return self.do(
            played_by,
            f"player activates buff {card_id} on f-0-2, {direction} target's {stat} by {amt}",
            None,
        )

    def v1_prevent_rotation_continuous(
        self,
        card_id: str,
        played_by: str,
        target: str,
        target_attribute: T.Optional[str] = None,
        target_value: T.Optional[T.Any] = None,
    ):
        """card targets something, preventing card rotation (ATK/DEF stance) - continuously

        @since ?
        """
        # @todo will need a universal target resolving approach
        if target_attribute is not None and target.startswith("f-"):
            _, row, col = target.split("-")
            card: Card = Card(
                data=freeze(self.fields[int(row)][int(col)]),
                mapping=m(**{k: (v, None) for k, v in DefaultCardMapping.items()}),
            )
            actual_value: T.Any = card.get(target_attribute)
            # assert target[target_attribute] == target_value
            if target_value != actual_value:
                raise Exception(
                    f"""Cannot apply v1_prevent_rotation_continuous on {card.get("name")} - {target_value} <> {actual_value}"""
                )

        return self.do(
            played_by,
            f"player applies continuous effect {card_id} on {target}, preventing rotation",
            None,
        )

    def v1_prevent_rotation_N_times(
        self,
        card_id: str,
        played_by: str,
        num_of_turns: int,
        target: str,
        target_attribute: T.Optional[str] = None,
        target_value: T.Optional[T.Any] = None,
    ):
        """card targets something, preventing card rotation (ATK/DEF stance) - N-turns

        @since ?
        """
        target = None
        return self.do(
            played_by,
            f"player applies {num_of_turns}-turn effect {card_id} on {target}, preventing rotation",
            None,
        )

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


class Nemesis(Player):
    """bot behavior

    @since ?
    """

    def do(self, match: Match) -> bool:
        """do something

        @param match
        @param responses, a list of engine approved responses the bot can make
               to the latest event in the turn
        """

        positions: list[list[str]] = [
            [f"f-{i}-{j}" for j, spot in enumerate(field) if spot is None]
            for i, field in enumerate(match.fields)
            if i < 3
        ]
        responses: PVector[str] = (
            match.responses[self.name] if self.name in match.responses.keys() else v()
        )

        # if 0 < len(responses):
        # choose one of the responses
        # return True

        if not match.get("is_turn", Target.Player, self.name):
            logging.warning("not my turn...")
            return match

        # play the turn
        options: list = []
        for action, args in {
            "draw": "3",
        }.items():
            if match.get(f"can_{action}", Target.Player, self.name):
                options.append([self.name, action, args])

        while 1 > len(match.players[self.name].hand):
            logging.warning("waiting for hand draw")
            time.sleep(1)

        if any(positions):
            for event in [
                f"bot plays card {random.choice(match.players[self.name].hand)} to field position {random.choice(random.choice(positions))}"
            ]:
                options.append([self.name, event, None])

        time.sleep(random.randint(1, 7))
        if 0 < len(options):
            chose = random.choice(options)

            # do and end turn
            return match.do(*chose).do(self.name, "end_turn", None)

        # skip turn
        return match.do(self.name, "end_turn", None)
