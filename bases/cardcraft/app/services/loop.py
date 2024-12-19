import asyncio
import logging
import multiprocessing
import signal
import sys

from multiprocessing.synchronize import Lock as LockT

from cardcraft.game.loop import loop
from cardcraft.game.engine import DemoEngine


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
                await loop(DemoEngine)

    asyncio.run(game())
