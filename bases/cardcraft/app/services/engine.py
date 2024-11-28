import asyncio
import functools
import logging
import multiprocessing
import os
import time
import signal
import sys
import time
import typing as T

from multiprocessing.synchronize import Lock as LockT

from cardcraft.game.engine import BaseEngine
from cardcraft.game.loop import loop
from cardcraft.game.system import Event, Match, Target


class Engine(BaseEngine):
    async def parse(self, match: Match, event: Event):
        """parses free-text event and performs match state updates

        @since ?
        """
        entity, entry, *_ = event

        # parsers

        var = lambda e, vname: e

        # fmt: off
        # "$me plays card 123 to field position XYZ"

        # "player returns card 123 to hand"

        # "player uses 8c3c71cdfb1ebe8d14d00c49d4f11051 to attack unit-bot1"
        # fmt: on

        print([event, entry])

        # detect and process card movement
        if "plays card " in entry and "position " in entry:
            # fmt: off
            card_id = list(entry[entry.index("plays card ")+1])
            target_id = list(entry[entry.index("position ")+1])
            # fmt: on

            cid: str = "".join(card_id)
            card: dict = await self.card({"id": cid})

            _, *_t = target_id
            t: T.Iterable[T.Union[str, int]] = map("".join, _t)

            print([cid, card])

            # def resolution(match: Match):
            if cid not in match.players[entity]["hand"]:
                logging.warning(f"{entity} tried to play a card not in hand")
                return False

            match.players[entity]["hand"].pop(match.players[entity]["hand"].index(cid))
            *path, tail = map(int, t)

            functools.reduce(lambda a, e: a[e], path, match.fields)[tail] = card  # type: ignore[arg-type, return-value, call-overload]

            # self.resolutions.append(resolution)

        # detect and register attacks
        if " uses card " in entry and " to attack " in entry:
            card_id = list(entry[entry.index(" uses card ") + 1])
            target_id = list(entry[entry.index(" to attack ") + 1])

            opponent: str = "".join(target_id)  # type: ignore[no-redef]
            cid: str = "".join(card_id)  # type: ignore[no-redef]
            atk: int = int((await self.card({"id": cid})).get("E_value"))

            print([opponent, cid, atk])

            def resolution(match: Match):
                if opponent in match.players:
                    # attacks the opponent directly
                    match.players[opponent]["hp"] -= atk

            self.resolutions.append(resolution)

        # detect possible responses
        # ...


def locked_loop(lock: LockT):
    """the game loop

    @since ?

    @todo refer some things from memory to prevent object instantation
          and release on every single iteration
    """

    async def game():
        run: bool = True

        def stop(*a):
            run = False
            sys.exit()

        signal.signal(signal.SIGINT, stop)
        refresh: float = 0.6

        with lock:
            while run:
                await loop(Engine)

    asyncio.run(game())
