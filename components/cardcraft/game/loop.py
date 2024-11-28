import asyncio
import time

from cardcraft.game.engine import Engine
from cardcraft.game.db import gamedb
from cardcraft.game.nemesis import Nemesis
from cardcraft.game.system import Match, Target

engines: dict[str, Engine] = {}
refresh: int = 1


async def loop(engine_klass):
    async for match in gamedb.matches.find({"finished": None, "winner": None}):
        state = Match.create(match)

        if match["id"] not in engines:
            engines[match["id"]] = engine_klass()

        changed = await engines[match["id"]].process(state)

        if changed:
            state = changed

        if state.winner is None:
            opkey: T.Optional[str] = next(
                filter(
                    lambda e: e is not None and e.startswith("bot"),
                    state.players.keys(),
                ),
                None,
            )
            if opkey is not None and state.get("is_turn", Target.Player, opkey):
                Nemesis(opkey).do(match=state)
                changed = state

        then = state._asdict()

        if changed:
            await gamedb.matches.replace_one({"id": then["id"]}, then)

        await asyncio.sleep(refresh)

    time.sleep(refresh)
