import logging
import random
import time
import typing as T

from pyrsistent import PVector, v
from cardcraft.game.system import Match, Target


class Nemesis:
    """bot behavior

    @since ?
    """

    # player ID, for bots it is bot1, bot2 etc
    name: str

    def __init__(self, name: str):
        self.name = name

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
            return False

        # play the turn
        options: list = []
        for action, args in {
            "draw": "3",
        }.items():
            if match.get(f"can_{action}", Target.Player, self.name):
                options.append([self.name, action, args])

        while 1 > len(match.players[self.name]["hand"]):
            time.sleep(1)

        for event in [
            f"bot plays card {random.choice(match.players[self.name]['hand'])} to field position {random.choice(random.choice(positions))}"
        ]:
            options.append([self.name, event, None])

        time.sleep(random.randint(1, 7))
        if 0 < len(options):
            chose = random.choice(options)
            match.do(*chose)

            # end turn
            match.do(self.name, "end_turn", None)
            return True

        # skip turn
        match.do(self.name, "end_turn", None)
        return False
