import unittest

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from cardcraft.app.services.engine import Engine

card: dict = {
    "id": "abc123",
    "E_key": "atk",
    "E_value": 300
}

class TestEngine(unittest.IsolatedAsyncioTestCase):

    @patch("cardcraft.app.services.engine.Engine.card", new=AsyncMock(return_value=card))
    async def test_engine_moves_card_to_appropriate_position_when_card_movement_is_parsed(self):
        match = SimpleNamespace(
            fields=[
                [None, None, None], [None, None, None], [None, None, None],
                [None, None, None], [None, None, None], [None, None, None]
            ],
            cursor=[0, 0],
            turns=[[]],
            players={
                "xyz": {
                    "hand": ["abc123", "XYZ"]
                }
            }
        )

        match.turns[-1].append(["xyz", "$me plays card abc123 to field position f-3-0", None])
        processed = await Engine().process(match)

        self.assertEquals(card, match.fields[3][0])

    @patch("cardcraft.app.services.engine.Engine.card", new=AsyncMock(return_value=card))
    async def test_engine_reduces_player_hp_after_parsed_attack(self):
        
        match = SimpleNamespace(
            cursor=[0, 0],
            turns=[[
               [ "xyz", "player uses abc123 to attack unit-bot1", None]
            ]],
            players={
                "xyz": {
                    "hand": ["abc123", "XYZ"]
                },
                "bot1": {
                    "hand": [],
                    "hp": 5_000
                }
            }
        )
        
        target = "bot1"
        hp_before = match.players[target]["hp"]

        engine = Engine()
        processed = await engine.process(match)
        engine.resolve(match)

        self.assertEquals(hp_before - card["E_value"], match.players[target]["hp"])

    async def test_engine_prevents_attack_from_noncontrolled_cards(self):

        
        self.assertTrue(False)