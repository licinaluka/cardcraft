import logging
import random
import typing as T

from cardcraft.app.services.match import Match, Target


class Nemesis:
    """bot behavior

    @since ?
    """

    # player ID, for bots it is bot1, bot2 etc
    name: str

    def __init__(self, name: str):
        self.name = name

    def do(self, match: Match, responses: list[str] = None) -> bool:
        """do something

        @param match
        @param responses, a list of engine approved responses the bot can make
               to the latest event in the turn
        """
        positions: list[list[str]] = [
            [f"f-{i}-{j}" for j in range(0, 3)] for i in range(0, 3)
        ]
        responses = match.responses.get(self.name, [])

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

        for event in [
            f"bot plays card {random.choice(match.players[self.name]['hand'])} to field position {random.choice(random.choice(positions))}"
        ]:
            options.append([self.name, event, None])

        # time.sleep(random.randint(1, 3))
        if 0 < len(options):
            match.do(*random.choice(options))

            # end turn
            match.do(self.name, "end_turn", None)
            return True

        # skip turn
        match.do(self.name, "end_turn", None)
        return False