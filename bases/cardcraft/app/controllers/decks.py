import os
import typing as T

from flask import Blueprint, redirect, request
from pyhiccup.core import _convert_tree, html
from werkzeug.datastructures.structures import ImmutableMultiDict

from cardcraft.app.controllers.cards import card
from cardcraft.app.views.base import hiccpage, trident
from cardcraft.app.views.navigation import menu
from cardcraft.app.services.db import gamedb
from cardcraft.app.services.mem import mem

controller = Blueprint("decks", __name__)


@controller.route("/decks", methods=["GET"])
async def list_decks():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    decks = await gamedb.decks.find({"owner": identity}).to_list()
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
        listing = [
            [
                "a",
                {"hx-get": f"/web/part/game/decks/{e['id']}", "hx-target": ".tertiary"},
                f"{e['name']}, ({len(e['cards'])})",
            ]
            for e in decks
        ]

    return await hiccpage([trident(menu(), listing, ["p", "No deck selected"])])


@controller.route("/web/part/game/decks/<deck_id>", methods=["GET"])
async def show_deck(deck_id: str):
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    deck: T.Optional[dict] = await gamedb.decks.find_one({"id": deck_id, "owner": identity})

    if deck is None:
        raise Exception('Deck not found!')

    used: list = await gamedb.cards.find({"id": {"$in": deck["cards"]}}).to_list()

    used_ids: list = list(map(lambda e: e["id"], used))
    used_view: list = [card(e) for e in used] or ["p", "Put cards here"]

    available: list = list(
        filter(lambda e: e["id"] not in used_ids, await gamedb.cards.find({}).to_list())
    )

    available_view: list = [card(e) for e in available] or [
        "p",
        "No unused cards availble",
    ]

    return _convert_tree(
        [
            "div",
            {"class": "game"},
            ["h3", "Deck builder"],
            [
                "div",
                {
                    "style": "display:flex;flex-direction:row;justify-content:space-between;",
                },
                [
                    [
                        "form",
                        {
                            "hx-put": f"/web/part/game/decks/{deck_id}",
                            "hx-target": ".tertiary",
                            "style": "flex-grow: 1; height: 90vh; overflow-y: scroll; margin: 1em; padding: 1em;",
                        },
                        [
                            [
                                "input",
                                {
                                    "type": "text",
                                    "name": "name",
                                    "value": deck["name"],
                                    "placeholder": "Deck name",
                                },
                            ],
                            ["input", {"type": "submit"}],
                            ["hr"],
                            [
                                "div",
                                [
                                    [
                                        "div",
                                        {
                                            "class": "deck-view spot",
                                            "style": "overflow-y:scroll;",
                                            "ondrop": "drop(event)",
                                            "ondragover": "allowDrop(event)",
                                            "onclick": "move(event)",
                                            "style": "background: #111; padding-bottom: 5em;",
                                        },
                                        [["p", "deck view:"], used_view],
                                    ]
                                ],
                            ],
                        ],
                    ],
                    [
                        "div",
                        {
                            "class": "cards-view spot",
                            "style": "overflow-y:scroll;",
                            "ondrop": "drop(event)",
                            "ondragover": "allowDrop(event)",
                            "onclick": "move(event)",
                            "style": "background: #111; padding-bottom: 5em; flex-grow: 1; height: 90vh; overflow-y: scroll; margin: 1em; padding: 1em;",
                        },
                        [
                            ["p", "available cards:"],
                            available_view,
                        ],
                    ],
                ],
            ],
        ]
    )


@controller.route("/web/part/game/decks/new", methods=["POST"])
async def store_deck():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    form: ImmutableMultiDict[str, str] = request.form
    if form is None:
        raise Exception('Form not sent!')

    name: T.Optional[str] = form.get("name")

    if name is None:
        raise Exception('Name is missing!')

    cards: list[str] = form.getlist("card")

    await gamedb.decks.insert_one(
        {"id": os.urandom(16).hex(), "name": name, "cards": cards, "owner": identity}
    )

    return redirect("/decks", code=303)


@controller.route("/web/part/game/decks/<deck_id>", methods=["PUT"])
async def update_deck(deck_id: str):
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    form: ImmutableMultiDict[str, str] = request.form

    if form is None:
        raise Exception('Form not sent!')

    name: T.Optional[str] = form.get("name")

    if name is None:
        raise Exception('Name is missing!')

    cards: T.Optional[list[str]] = form.getlist("card")

    if cards is None:
        raise Exception('Cards are missing!')

    await gamedb.decks.update_one(
        {"id": deck_id}, {"$set": {"name": name, "cards": cards, "owner": identity}}
    )

    return await show_deck(deck_id)


@controller.route("/web/part/game/decks/new", methods=["GET"])
async def new_deck():
    available: list = await gamedb.cards.find({}).to_list()

    return html(
        [
            "div",
            {"class": "game"},
            ["h2", "deck builder"],
            [
                "div",
                {
                    "style": "display:flex;flex-direction:row;justify-content:space-evenly;",
                },
                [
                    [
                        "form",
                        {"hx-post": "/web/part/game/decks/new", "hx-target": "body"},
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
                                [
                                    [
                                        "div",
                                        {
                                            "class": "deck-view spot",
                                            "style": "overflow-y:scroll;",
                                            "ondrop": "drop(event)",
                                            "ondragover": "allowDrop(event)",
                                            "onclick": "move(event)",
                                        },
                                        [["p", "deck view:"]],
                                    ]
                                ],
                            ],
                        ],
                    ],
                    [
                        "div",
                        {
                            "class": "cards-view spot",
                            "style": "overflow-y:scroll;",
                            "ondrop": "drop(event)",
                            "ondragover": "allowDrop(event)",
                            "onclick": "move(event)",
                        },
                        [
                            ["p", "available cards:"],
                            [card(e) for e in available],
                        ],
                    ],
                ],
            ],
        ]
    )
