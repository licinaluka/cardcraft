import asyncio

from expects import expect, be, equal
from mamba import describe, context, it
from pyrsistent import freeze, m, v

from cardcraft.game.engine import DemoEngine
from cardcraft.game.loop import tick
from cardcraft.game.system import Card, Match

with describe("system"):
    with context("match class:"):
        with it("can query any card on the field about its positioning/orientation"):

            card1 = {
                "id": "something",
                "_faceup": True,
                "_orientation": -90,
                "E_value": 1200,
                "F_value": 800,
            }

            match = Match.create(
                dict(
                    id="abc123",
                    cursor=v(0, 0),
                    fields=v(v(card1)),
                    players=m(),
                    turns=v(),
                )
            )
            final = asyncio.run(tick(match.serialize(), DemoEngine, persists=False))

            card = Card(data=final.fields[0][0], mapping=m())
            expected = (True, -90)
            actual = (card.get("faceup"), card.get("orientation"))
            expect(actual).to(equal(expected))
