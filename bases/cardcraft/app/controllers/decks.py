import os

from flask import Blueprint, redirect, request
from pyhiccup.core import _convert_tree, html

from cardcraft.app.controllers.cards import card
from cardcraft.app.views.base import hiccpage, trident
from cardcraft.app.views.navigation import menu
from cardcraft.app.services.db import gamedb

controller = Blueprint("decks", __name__)


@controller.route("/decks", methods=["GET"])
async def list_decks():
    decks = await gamedb.decks.find({}).to_list()
    listing: list = [
        "p",
        {"class": "blank"},
        [
            ["span", "No decks!"],
            [
                "a",
                {"hx-get": "/web/part/game/decks/new", "hx-target": ".tertiary"},
                "create one",
            ],
        ],
    ]

    if 0 < len(decks):
        listing = [["p", f"deck: {e['id']}"] for e in decks]

    return hiccpage(
        [
            trident(menu(), listing, ["p", "No deck selected"]),
        ]
    )


@controller.route("/decks/<deck_id>", methods=["GET"])
async def show_deck(deck_id: str):
    return _convert_tree(["p", "deck"])

@controller.route("/web/part/game/decks/new", methods=["POST"])
async def store_deck():
    name: str = request.form.get("name")
    cards: dict = request.form.getlist("card")

    await gamedb.decks.insert_one({"id": os.urandom(16).hex(), "name": name, "cards": cards})

    return redirect("/decks")


@controller.route("/web/part/game/decks/new", methods=["GET"])
async def new_deck():
    available: list = await gamedb.cards.find({}).to_list()

    return html(
        [
            "div",
            {"class": "game"},
            [
                ["h2", "deck builder"],
                [
                    "form",
                    {"hx-post": "/web/part/game/decks/new"},
                    [
                        [
                            "input",
                            {
                                "type": "text",
                                "name": "name",
                                "placeholder": "Deck name",
                            },
                        ],
                        ["input", {"type": "submit"}],
                        [
                            "div",
                            {
                                "style": "display:flex;flex-direction:row;justify-content:space-evenly;"
                            },
                            [
                                [
                                    "div",
                                    {
                                        "class": "deck-view",
                                        "style": "overflow-y:scroll;",
                                        "ondrop": "drop(event)",
                                        "ondragover": "allowDrop(event)",
                                    },
                                    [["p", "deck view:"]],
                                ]
                            ],
                            [
                                "div",
                                {
                                    "class": "cards-view",
                                    "style": "overflow-y:scroll;",
                                    "ondrop": "drop(event)",
                                    "ondragover": "allowDrop(event)",
                                },
                                [
                                    ["p", "available cards:"],
                                    [card(e) for e in available],
                                ],
                            ],
                        ],
                    ],
                ],
            ],
        ]
    )
