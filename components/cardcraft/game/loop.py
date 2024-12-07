import asyncio
import time
import typing as T

from pyrsistent import thaw

from cardcraft.game.engine import Engine
from cardcraft.game.db import gamedb
from cardcraft.game.system import Match, Nemesis, Target

engines: dict[str, Engine] = {}
refresh: int = 1


async def tick(match: dict, engine_klass: type, persists: bool = True) -> Match:
    state = Match.fromdict(match)

    if match["id"] not in engines:
        engines[match["id"]] = engine_klass()

    bot: T.Optional[str] = next(
        filter(
            lambda e: e.startswith("bot ") and state.get("is_turn", Target.Player, e),
            state.players.keys(),
        ),
        None,
    )

    if bot is not None:
        state = Nemesis(name=bot).do(match=state)

    changed = await engines[match["id"]].process(state)

    if changed:
        state = changed

    then = thaw(state.serialize())

    if changed and persists:
        await gamedb.matches.replace_one({"id": then["id"]}, then)

    await asyncio.sleep(refresh)
    return changed


async def loop(engine_klass):
    while True:
        async for match in gamedb.matches.find({"finished": None, "winner": None}):
            await tick(match, engine_klass)

        time.sleep(refresh)
