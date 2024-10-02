import unittest

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from cardcraft.app.services.engine import Engine

card: dict = {
    "id": "abc123"
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