import asyncio

from mamba import before, description, context, it, _it
from expects import be, contain, expect, equal
from pyrsistent import m, v, freeze, thaw
from random import randint
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from cardcraft.game.engine import DemoEngine
from cardcraft.game.loop import tick
from cardcraft.game.system import Match, Nemesis


async def cardcoro(ref: object, query: dict):
    return next(
        filter(
            lambda e: e["id"] == query["id"],
            [
                {"id": "abcdefgh", "E_value": 500},
                {"id": "abc123", "E_value": 500, "F_value": 800},
                {"id": "abc124", "E_value": 1700, "F_value": 200},
            ],
        )
    )


DemoEngine.card = cardcoro


with description("game engine") as self:
    with context("match init and finalization:"):
        with it("allows bots to play against each other"):
            # arrange
            match = Match.create(
                dict(
                    id="abc",
                    fields=v(v()),
                    players=m(
                        **{
                            "bot a": Nemesis(
                                name="bot a", hp=1000, hand=v("abc"), deck=m(cards=[])
                            ),
                            "bot b": Nemesis(
                                name="bot b", hp=0, hand=v("thing"), deck=m(cards=[])
                            ),
                        }
                    ),
                    responses=m(),
                    winner=None,
                    opener="bot a",
                    cursor=v(0, 0),
                    turns=v(v()),
                )
            )

            # act
            first = asyncio.run(tick(match.serialize(), DemoEngine, persists=False))
            final = asyncio.run(tick(first.serialize(), DemoEngine, persists=False))

            # assert
            expect(match.players.keys()).to(contain(final.winner))

    with context("player event parsing:"):
        with it("plays a card to field"):
            # arrange
            card_id = "abcdefgh"

            match = Match.create(
                dict(
                    id="abc",
                    fields=v(*(v(*(None for j in range(0, 5))) for i in range(0, 4))),
                    players=m(**{"playername": m(**{"hand": [card_id], "hp": 8000})}),
                    winner=None,
                    opener="playername",
                    cursor=v(0, 0),
                    turns=v(v()),
                )
            )

            row = randint(0, 3)
            col = randint(0, 3)

            # act
            did = match.do(
                "playername",
                f"player plays card {card_id} to field position f-{row}-{col}",
                None,
            )
            final = asyncio.run(DemoEngine().process(did))

            # assert
            expect(final.fields[row][col]).to(equal({"id": card_id}))

        with it("attacks opponent with a card"):
            # arrange
            match = Match.create(
                dict(
                    id="def",
                    fields=v(*(v(*(None for j in range(0, 5))) for i in range(0, 4))),
                    players=m(
                        **{"playername": m(**{"hp": 8000}), "what": m(**{"hp": 8000})}
                    ),
                    winner=None,
                    opener="playername",
                    cursor=v(0, 0),
                    turns=v(v()),
                )
            )

            card_id = "abcdefgh"
            opponent = "what"

            # act
            did = match.do(
                "playername",
                f"player uses card {card_id} to attack {opponent}",
                None,
            )
            turnin = did.do("playername", "end_turn", None)
            final = asyncio.run(DemoEngine().process(turnin))

            # assert
            expect(final.players.get(opponent).hp).to(equal(7500))

        with it("attacks opponent card with a weaker card, loses"):

            card_id = "abc123"
            target = SimpleNamespace(row=1, col=2)
            attacker = SimpleNamespace(row=2, col=1)

            fields = [[None for j in range(0, 5)] for i in range(0, 4)]

            fields[target.row][target.col] = {
                "id": "something",
                "E_value": 1200,
                "F_value": 800,
            }
            fields[attacker.row][attacker.col] = {
                "id": card_id,
                "E_value": 1100,
                "F_value": 200,
            }
            match = Match.create(
                dict(
                    id="def",
                    fields=freeze(fields),
                    players=m(
                        **{"playername": m(**{"hp": 8000}), "what": m(**{"hp": 8000})}
                    ),
                    winner=None,
                    opener="playername",
                    cursor=v(0, 0),
                    turns=v(v()),
                )
            )

            attack = match.do(
                "playername",
                f"player uses card {card_id} to attack f-{target.row}-{target.col}",
                None,
            )
            final = asyncio.run(DemoEngine().process(attack))

            expect(final.fields[attacker.row][attacker.col]).to(equal(None))

        with it("attacks opponent card with a stronger card, wins"):

            card_id = "abc124"
            target = SimpleNamespace(row=1, col=2)
            attacker = SimpleNamespace(row=2, col=1)

            fields = [[None for j in range(0, 5)] for i in range(0, 4)]

            fields[target.row][target.col] = {
                "id": "something",
                "E_value": 1200,
                "F_value": 800,
            }
            fields[attacker.row][attacker.col] = {
                "id": card_id,
                "E_value": 1700,
                "F_value": 200,
            }
            match = Match.create(
                dict(
                    id="def",
                    fields=freeze(fields),
                    players=m(
                        **{"playername": m(**{"hp": 8000}), "what": m(**{"hp": 8000})}
                    ),
                    winner=None,
                    opener="playername",
                    cursor=v(0, 0),
                    turns=v(v()),
                )
            )

            attack = match.do(
                "playername",
                f"player uses card {card_id} to attack f-{target.row}-{target.col}",
                None,
            )
            final = asyncio.run(DemoEngine().process(attack))

            expect(final.fields[target.row][target.col]).to(equal(None))
