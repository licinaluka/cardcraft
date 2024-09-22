import os
import random

from flask import Blueprint, Response, redirect, request
from pyhiccup.core import _convert_tree

from cardcraft.app.controllers.cards import card
from cardcraft.app.services.db import gamedb

controller = Blueprint("matches", __name__)


@controller.route("/web/part/game/matches", methods=["GET"])
async def list_matches():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

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
        {f"players.{sess_id}": {"$exists": True}}
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
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    match = await gamedb.matches.find_one(
        {"id": match_id, f"players.{sess_id}": {"$exists": True}, "finished": None}
    )
    assert match is not None

    deck = await gamedb.decks.find_one(
        {"id": match["players"][sess_id]["deck"]["id"], "owner": sess_id}
    )
    assert deck is not None

    hand: list[dict] = await gamedb.cards.find({"id": {"$in": deck["cards"]}}).to_list()

    pl = match["players"][sess_id]
    opkey = next(filter(lambda e: e != sess_id, match["players"].keys()), None)
    op = match["players"][opkey]

    resp = Response()
    resp.response = _convert_tree(
        [
            "div",
            {"class": "game"},
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
                                card({"A_value": "?", "D_value": "?", "C_value": None})
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
                    ],
                ],
            ],
        ]
    )

    return resp


@controller.route("/web/part/game/matches/new/decks", methods=["POST"])
async def new_match_deck_selection():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")
    assert sess_id is not None

    unfinished = await gamedb.matches.find(
        {f"players.{sess_id}": {"$exists": True}, "finished": None}
    ).to_list()

    if 0 < len(unfinished):
        raise Exception("You are already participating in a match!")

    decks: list[dict] = await gamedb.decks.find({"owner": sess_id}).to_list()
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
    deck_id: str = request.form.get("deck_id")
    deck_pl: T.Optional[dict] = await gamedb.decks.find_one(
        {"owner": sess_id, "id": deck_id}
    )

    assert sess_id is not None
    assert deck_pl is not None

    battle_ref: str = os.urandom(16).hex()

    unfinished = await gamedb.matches.find(
        {f"players.{sess_id}": {"$exists": True}, "finished": None}
    ).to_list()

    if 0 < len(unfinished):
        raise Exception("You are already participating in a match!")

    battle = await gamedb.games.find_one({"ref": battle_ref})

    if battle is not None:
        raise Exception("Error code 409")  # should not happen

    await gamedb.matches.insert_one(
        {
            "id": battle_ref,
            "players": {
                "bot1": {"hp": 100, "hpmax": 100, "name": "BOT1", "deck": deck_pl},
                sess_id: {"hp": 100, "hpmax": 100, "name": sess_id, "deck": deck_pl},
            },
            "finished": None,
        }
    )

    return redirect(f"/web/part/game/matches/{battle_ref}")
