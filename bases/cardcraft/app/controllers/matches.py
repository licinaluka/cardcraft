import json
import os
import random

from flask import Blueprint, Response, redirect, request
from pyhiccup.core import _convert_tree, html
from types import SimpleNamespace

from cardcraft.app.controllers.cards import card
from cardcraft.app.services.db import gamedb
from cardcraft.app.services.match import Match, Nemesis, Target
from cardcraft.app.services.mem import mem

controller = Blueprint("matches", __name__)


@controller.route("/web/part/game/matches", methods=["GET"])
async def list_matches():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    if identity is None:
        return _convert_tree(["p", "Not authenticated"])

    no_matches = [
        "div",
        {"class": "blank"},
        [
            [
                "div",
                {"style": "color: #888; cursor: default; user-select: none"},
                "No previous matches!",
            ],
        ],
    ]

    matches = await gamedb.matches.find(
        {f"players.{identity}": {"$exists": True}}
    ).to_list()

    return _convert_tree(
        [
            "div",
            [
                [
                    "a",
                    {
                        "hx-post": "/web/part/game/matches/new/decks",
                        "hx-target": ".tertiary",
                        "hx-swap": "innerHTML",
                        "class": "btn purple",
                    },
                    " Start a match!",
                ],
                [
                    "div",
                    {"class": "collection black"},
                    [
                        [
                            "a",
                            {
                                "hx-get": f"/web/part/game/matches/{e['id']}",
                                "hx-target": ".tertiary",
                                "class": "collection-item avatar",
                            },
                            [
                                "img",
                                {
                                    "src": f"/resources/app/img/card-back-ue-pirated.jpg",
                                    "class": "circle",
                                },
                            ],
                            ["span", {"class": "title"}, e["id"]],
                            # ["p", e["D_value"]],
                        ]
                        for e in matches
                    ]
                    or no_matches,
                ],
            ],
        ]
    )


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
        "finished": None,
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

    Nemesis(opkey).do(match=game)

    hand = await gamedb.cards.find(
        {"id": {"$in": game.players[identity]["hand"]}}
    ).to_list()

    resp = Response()
    resp.response = _convert_tree(
        [
            [
                "div",
                {"class": "game"},
                [
                    [
                        "a",
                        {
                            "class": "game-refresh-trigger",
                            "hx-get": f"/web/part/game/matches/{match_id}",
                            "hx-target": ".tertiary",
                            "hx-trigger": "every 5s",
                        },
                        "Refresh",
                    ],
                    [
                        "a",
                        {
                            "class": "btn danger",
                            "hx-post": f"/web/part/game/matches/{match_id}/do",
                            "hx-vals": "js:{"
                            + f"event: ['{identity}', 'end_turn', null]"
                            + "}",
                            "hx-ext": "json-enc",
                            "hx-trigger": "click",
                            "hx-swap": "none",
                        },
                        "End turn",
                    ],
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
                                        card(
                                            {
                                                "A_value": "?",
                                                "D_value": "?",
                                                "C_value": None,
                                            }
                                        )
                                        for e in range(0, random.randint(3, 7))
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
                                    {"class": "field"},
                                    [
                                        [
                                            "div",
                                            {
                                                "class": "spot",
                                                "ondrop": "drop(event)",
                                                "ondragover": "allowDrop(event)",
                                            },
                                            " ",
                                        ]
                                        for e in range(1, 6)
                                    ],
                                    [
                                        [
                                            "div",
                                            {
                                                "class": "spot",
                                                "ondrop": "drop(event)",
                                                "ondragover": "allowDrop(event)",
                                            },
                                            " ",
                                        ]
                                        for e in range(6, 11)
                                    ],
                                ],
                                ["div", {"class": "divider"}, " "],
                                [
                                    "div",
                                    {"class": "field"},
                                    [
                                        [
                                            "div",
                                            {
                                                "class": "spot",
                                                "ondrop": "drop(event)",
                                                "ondragover": "allowDrop(event)",
                                            },
                                            " ",
                                        ]
                                        for e in range(1, 6)
                                    ],
                                    [
                                        [
                                            "div",
                                            {
                                                "class": "spot",
                                                "ondrop": "drop(event)",
                                                "ondragover": "allowDrop(event)",
                                            },
                                            " ",
                                        ]
                                        for e in range(6, 11)
                                    ],
                                ],
                            ],
                        ],
                        [
                            "div",
                            {"class": "player"},
                            [
                                ["p", f"{pl['name']} {pl['hp']}/{pl['hpmax']}"],
                                ["div", {"class": "hand"}, [card(e) for e in hand]],
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
                                        else ["div", {"class": "deck-back-render"}, " "]
                                    )
                                    for i, _ in enumerate(deck)
                                ] if 0 < len(deck) else ["p", "No cards left in deck"],
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
                    ["input", {"type": "submit"}],
                ],
            ],
        ]
    )


@controller.route("/web/part/game/matches/new", methods=["POST"])
async def new_match():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    deck_id: str = request.form.get("deck_id")
    deck_pl: T.Optional[dict] = await gamedb.decks.find_one(
        {"owner": identity, "id": deck_id}
    )

    assert deck_pl is not None

    battle_ref: str = os.urandom(16).hex()

    unfinished = await gamedb.matches.find(
        {f"players.{identity}": {"$exists": True}, "finished": None}
    ).to_list()

    if 0 < len(unfinished):
        raise Exception("You are already participating in a match!")

    battle = await gamedb.games.find_one({"ref": battle_ref})

    if battle is not None:
        raise Exception("Error code 409")  # should not happen

    players = ["bot1", identity]
    opener = random.choice(players)
    second = next(e for e in players if e != opener)
    await gamedb.matches.insert_one(
        {
            "id": battle_ref,
            "players": {
                "bot1": {
                    "hp": 50000,
                    "hpmax": 5000,
                    "name": "BOT1",
                    "deck": deck_pl,
                    "hand": [],
                },
                identity: {
                    "hp": 50000,
                    "hpmax": 5000,
                    "name": sess_id,
                    "deck": deck_pl,
                    "hand": [],
                },
            },
            "opener": opener,
            "finished": None,
            "cursor": [0, 0],
            "turns": [[[opener, "draw", 5], [second, "draw", 5]]],  # turn 1  # turn 2
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
    assert identity == e

    lookup = {
        "id": match_id,
        f"players.{identity}": {"$exists": True},
        "finished": None,
    }
    match = await gamedb.matches.find_one(lookup)
    assert match is not None

    game = Match.create(match)
    game.do(e, a, v)

    await gamedb.matches.replace_one(lookup, game._asdict())

    return []
