import logging
import typing as T

from cardcraft.app.services.match import Match, Target

class Nemesis:
    name: str

    def __init__(self, name: str):
        self.name = name

    def do(self, match: Match) -> bool:
        """do something"""

        if not match.get("is_turn", Target.Player, self.name):
            logging.warning("not my turn...")
            return False

        options: list = []
        for action, args in {
            "draw": "3",
        # "play": random.choice(match.players[self.name]["hand"]),
        }.items():
            if match.get(f"can_{action}", Target.Player, self.name):
                options.append([self.name, action, args])

        # time.sleep(random.randint(1, 3))
        if 0 < len(options):
            match.do(*random.choice(options))

            # end turn
            match.do(self.name, "end_turn", None)
            return True

        # skip turn
        match.do(self.name, "end_turn", None)
        return False
