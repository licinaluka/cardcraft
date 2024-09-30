import functools
import json
import math
import os
import random
import time

from flask import Blueprint, Response, redirect, request
from pyhiccup.core import _convert_tree, html
from types import SimpleNamespace

from cardcraft.app.controllers.cards import card
from cardcraft.app.services.db import gamedb
from cardcraft.app.services.game import Match, Target
from cardcraft.app.services.nemesis import Nemesis
from cardcraft.app.services.mem import mem
from cardcraft.app.services.pot import pot
from cardcraft.app.views.matches import listed, shown

controller = Blueprint("matches", __name__)


@controller.route("/web/part/game/matches", methods=["GET"])
async def list_matches():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    if identity is None:
        return _convert_tree(["p", "Not authenticated"])

    matches = await gamedb.matches.find(
        {f"players.{identity}": {"$exists": True}}
    ).to_list()

    return _convert_tree(listed(matches))


@controller.route("/web/part/game/matches/<match_id>", methods=["GET"])
async def show_match(match_id: str):
    """main match screen

    @version 2024-09-22
    """
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    lookup = {
        "id": match_id,
        f"players.{identity}": {"$exists": True},
    }
    match = await gamedb.matches.find_one(lookup)
    assert match is not None

    game = Match.create(match)

    deck: list[dict] = await gamedb.cards.find(
        {"id": {"$in": game.players[identity]["deck"]["cards"]}}
    ).to_list()

    pl = game.players[identity]
    opkey = next(filter(lambda e: e != identity, match["players"].keys()), None)
    op = game.players[opkey]

    hand = await gamedb.cards.find(
        {"id": {"$in": game.players[identity]["hand"]}}
    ).to_list()

    ophand = await gamedb.cards.find(
        {"id": {"$in": game.players[opkey]["hand"]}}
    ).to_list()

    # fields = {
    #     e["id"]: e
    #     for e in await gamedb.cards.find(
    #         {"id": {"$in": [e for f in game.fields for e in f if e is not None]}}
    #     ).to_list()
    # }

    resp = Response()
    resp.response = _convert_tree(
        [
            [
                "div",
                {"class": "game", "id": "game"},
                [
                    ["div", {"id": "loading", "class": "shown"}, " "],
                    [
                        "a",
                        {
                            "class": "btn purple game-refresh-trigger",
                            "hx-get": f"/web/part/game/matches/{match_id}",
                            "hx-target": ".tertiary",
                            "hx-trigger": "click, every 9s",
                        },
                        "Refresh",
                    ],
                    ["span", " | "],
                    [
                        "a",
                        {
                            "class": "btn red",
                            "hx-post": f"/web/part/game/matches/{match_id}/do",
                            "hx-vals": "js:{"
                            + f"event: ['{identity}', 'end_turn', null]"
                            + "}",
                            "hx-ext": "json-enc",
                            "hx-trigger": "click",
                            "hx-swap": "none",
                        },
                        "End turn",
                    ] if game.get('is_turn', Target.Player, identity) else (["small", "Opponent turn"] if game.winner is None else ["small", f"{game.winner} WON"]),
                    ["span", " | "],
                    [
                        "p", {"class": "btn grey"},
                        await show_match_pot_status(match_id),
                    ],
                    ["p", {"class": "btn blue lighten-2"}, "PASS"] if game.get("can_respond", Target.Player, identity) else ["small", "/"],
                    [
                        "div",
                        {"class": "board"},
                        [
                            "div",
                            {"class": "opponent"},
                            [
                                ["p", f"{op['name']} {op['hp']}/{op['hpmax']}"],
                                [
                                    "div",
                                    {"class": "hand"},
                                    [
                                        [
                                            "div",
                                            {"class": "card-container"},
                                            card(
                                                {
                                                    "A_value": "?",
                                                    "D_value": "?",
                                                    "C_value": None,
                                                }
                                            ),
                                        ]
                                        for i, e in enumerate(ophand)
                                    ],
                                ],
                            ],
                        ],
                        [
                            "div",
                            {"class": "battle", "id": "battle"},
                            [
                                ["p", "BAT"],
                                [
                                    "div",
                                    {"id": f"unit-bot1"},
                                    [
                                        "div",
                                        {
                                            "class": "spot",
                                            "ondrop": "drop(event)",
                                            "ondragover": "allowDrop(event)",
                                            "onclick": "move(event)",
                                        },
                                        card(
                                            {
                                                "id": "something",
                                                "A_value": op["name"],
                                                "C_value": "elemental-interception.jpeg",
                                                "D_value": "Pro card player, trained specifically to challenge you",
                                            }
                                        ),
                                    ],
                                ],
                                [
                                    [
                                        "div",
                                        {"class": "field"},
                                        [
                                            [
                                                "div",
                                                {"id": f"f-{i}-{j}"},
                                                [
                                                    "div",
                                                    {
                                                        "class": "spot"
                                                        + (
                                                            " grey darken-4"
                                                            if (
                                                                i
                                                                < (len(game.fields) / 2)
                                                                and j < (len(field))
                                                            )
                                                            else ""
                                                        ),
                                                        "ondrop": "drop(event)",
                                                        "ondragover": "allowDrop(event)",
                                                        "onclick": "move(event)",
                                                    },
                                                    (
                                                        card(game.fields[i][j])
                                                        if spot is not None
                                                        else " "
                                                    ),
                                                ],
                                            ]
                                            for j, spot in enumerate(field)
                                        ],
                                    ]
                                    for i, field in enumerate(game.fields)
                                ],
                            ],
                        ],
                        [
                            "div",
                            {"class": "player"},
                            [
                                ["p", f"{pl['name']} {pl['hp']}/{pl['hpmax']}"],
                                [
                                    "div",
                                    {"class": "hand"},
                                    [
                                        [
                                            "div",
                                            {"class": "card-container"},
                                            card(dict(e, handidx=i)),
                                        ]
                                        for i, e in enumerate(hand)
                                    ],
                                ],
                                (
                                    [
                                        (
                                            [
                                                "div",
                                                {
                                                    "class": "deck-back-render glow",
                                                    "hx-post": f"/web/part/game/matches/{match_id}/do",
                                                    "hx-vals": "js:{"
                                                    + f"event: ['{identity}', 'draw', '1']"
                                                    + "}",
                                                    "hx-ext": "json-enc",
                                                    "hx-trigger": "click",
                                                    "hx-swap": "none",
                                                },
                                                " ",
                                            ]
                                            if (
                                                game.get(
                                                    "is_turn",
                                                    Target.Player,
                                                    identity,
                                                )
                                                and i == (len(deck) - 1)
                                            )
                                            else ["div", {"class": "deck-back-render"}]
                                        )
                                        for i, _ in enumerate(deck)
                                    ]
                                    if 0 < len(deck)
                                    else ["p", "No cards left in deck"]
                                ),
                            ],
                        ],
                    ],
                ],
            ]
        ]
    )

    return resp


@controller.route("/web/part/game/matches/new/decks", methods=["POST"])
async def new_match_deck_selection():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    unfinished = await gamedb.matches.find(
        {f"players.{identity}": {"$exists": True}, "finished": None}
    ).to_list()

    if 0 < len(unfinished):
        raise Exception("You are already participating in a match!")

    decks: list[dict] = await gamedb.decks.find({"owner": identity}).to_list()
    if 0 < len(decks):
        # player has no decks, use a pre-defined starter deck
        pass

    return _convert_tree(
        [
            "div",
            {"class": "game"},
            [
                "form",
                {"hx-post": "/web/part/game/matches/new", "hx-target": ".game"},
                [
                    [
                        "select",
                        {"class": "browser-default", "name": "deck_id"},
                        [
                            [
                                [
                                    "label",
                                    {"for": "#deck-selector"},
                                    [
                                        "option",
                                        {
                                            "id": "deck-selector",
                                            "type": "radio",
                                            "value": deck["id"],
                                        },
                                        deck["name"],
                                    ],
                                ],
                            ]
                            for deck in decks
                        ],
                    ],
                    ["small", {"class": "red-text"}, "*Required"],
                    ["br"],
                    [
                        "label",
                        {"for": "#pot-lamports"},
                        [
                            [
                                "input",
                                {
                                    "id": "pot-lamports",
                                    "type": "number",
                                    "name": "lamports",
                                    "min": pot.get_pot_fee(1),
                                    "placeholder": "Lamports to put in match pot",
                                    "hx-trigger": "change, keyup",
                                    "hx-target": "#pot-message",
                                    "hx-post": "/web/part/game/matches/new/pot-fee",
                                    "hx-ext": "json-enc",
                                },
                            ],
                            ["span", {"id": "pot-message"}, " "],
                        ],
                    ],
                    ["br"],
                    ["input", {"type": "hidden", "name": "txsig"}],
                    ["br"],
                    [
                        "a",
                        {
                            "class": "btn purple darken-1",
                            "onclick": f"window.purse.pot('{pot.sys.pubkey()}', document.querySelector('#pot-lamports').value)",
                        },
                        "Add to pot",
                    ],
                    ["span", " | "],
                    [
                        "button",
                        {"class": "btn purple lighten-1", "type": "submit"},
                        "Start",
                    ],
                ],
            ],
        ]
    )


@controller.route("/web/part/game/matches/new/pot-fee", methods=["POST"])
async def new_match_pot_fee():
    amount: int = int(request.json.get("lamports") or 0)
    fee: int = pot.get_pot_fee(amount)
    is_ok: bool = (fee * 1.2) < amount

    return _convert_tree(
        [
            "span",
            {"id": "pot-message", "class": "green-text" if is_ok else "red-text"},
            f"Minimum fees expected: {fee} Lamports",
        ]
    )


# @controller.route("/web/part/game/matches/<match_id>/pot-status", methods=["GET"])
async def show_match_pot_status(match_id: str):
    """checks pot status, pays winner, if any

    @todo move match win payout elsewhere
    """
    match: dict = await gamedb.matches.find_one({"id": match_id})

    total: int = 0

    for name in match["players"].keys():
        _: dict = match["players"][name]["pot"]
        if _["txsig"] is not None and _["lamports"] > 0:
            total += pot.get_transaction_details(
                _["txsig"], commitment="confirmed"
            ).amount

    if match["winner"] is not None:
        trunc: str = match["winner"][0:7]
        return f"PAID: {trunc}... AMOUNT: {total}"

    return f"POT: {total}"


@controller.route("/web/part/game/matches/new", methods=["POST"])
async def new_match():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    # deck selection
    deck_id: str = request.form.get("deck_id")
    deck_pl: T.Optional[dict] = await gamedb.decks.find_one(
        {"owner": identity, "id": deck_id}
    )

    # shuffle the decks
    deck_op = deck_pl
    random.shuffle(deck_op["cards"])
    random.shuffle(deck_pl["cards"])

    assert deck_pl is not None

    # pot
    pot: bool = request.form.get("pot") or False
    lamports: int = 0 if not pot else int(request.form.get("lamports") or 0)
    txsig: T.Optional[str] = request.form.get("txsig") or None

    # create match
    battle_ref: str = os.urandom(16).hex()

    unfinished = await gamedb.matches.find(
        {f"players.{identity}": {"$exists": True}, "finished": None}
    ).to_list()

    if 0 < len(unfinished):
        raise Exception("You are already participating in a match!")

    battle = await gamedb.matches.find_one({"ref": battle_ref})

    if battle is not None:
        raise Exception("Error code 409")  # should not happen

    players = ["bot1", identity]
    opener = random.choice(players)
    second = next(e for e in players if e != opener)

    # resolve bot pot
    lookup = {"players.bot1": {"$exists": True}, "player.bot1.txsig": {"$ne": None}}

    prev: list[dict] = (
        await gamedb.matches.find(lookup).sort({"started": -1}).limit(1).to_list()
    )
    prev_pot: dict = next(iter(prev), {})

    limit: int = int(os.getenv("BOT_POT_LAMPORT_MAX", 0))
    derived: int = math.ceil(
        0.5
        * min(
            limit,
            (
                functools.reduce(
                    lambda a, e: a.get(e, {}),
                    ["players", "bot1", "pot", "lamports"],
                    prev_pot,
                )
                or 0
            ),
        )
    )

    # has the amount
    if derived > 0:
        if pot.get_bot_balance(idx=1) <= derived:
            derived = 0

    # check if the amount makes sense
    if derived > 0:
        if (pot.get_pot_fee(derived) * 5) >= derived:
            derived = 0

    await gamedb.matches.insert_one(
        {
            "id": battle_ref,
            "fields": [[None for spot in range(0, 3)] for field in range(0, 6)],
            "players": {
                "bot1": {
                    "pot": {"lamports": derived, "txsig": None},
                    "hp": 5_000,
                    "hpmax": 5_000,
                    "name": "BOT1",
                    "deck": deck_op,
                    "hand": [],
                },
                identity: {
                    "pot": {"lamports": lamports, "txsig": txsig},
                    "hp": 5_000,
                    "hpmax": 5_000,
                    "name": sess_id,
                    "deck": deck_pl,
                    "hand": [],
                },
            },
            "responses": {},
            "opener": opener,
            "winner": None,
            "created": int(time.time()),
            "finished": None,
            "cursor": [0, 0],
            "turns": [[[opener, "draw", 3], [second, "draw", 3]]],  # turn 1  # turn 2
            "futures": {},
        }
    )

    return redirect(f"/web/part/game/matches/{battle_ref}")


@controller.route("/web/part/game/matches/<match_id>/do", methods=["POST"])
async def match_add_event(match_id: str):
    e, a, v = request.json.get("event")

    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    if e == "$me":
        e = identity

    assert identity == e

    lookup = {
        f"players.{identity}": {"$exists": True},
        "finished": None,
    }

    if match_id != "current":
        lookup["id"] = match_id

    match = await gamedb.matches.find_one(lookup)
    assert match is not None

    game = Match.create(match)
    game.do(e, a, v)

    await gamedb.matches.replace_one(lookup, game._asdict())

    return []
