import os
import typing as T

from flask import Blueprint, current_app, request, send_from_directory
from os.path import join
from pyhiccup.core import _convert_tree, html
from werkzeug.utils import secure_filename

from cardcraft.app.services.db import gamedb
from cardcraft.app.services.game import Match
from cardcraft.app.views.base import hiccpage, trident
from cardcraft.app.views.cards import (
    card,
    listed,
    creation_complexity,
    creation_detailed,
)
from cardcraft.app.views.navigation import menu, navigation

controller = Blueprint("cards", __name__)

demo = [
    {
        "A_key": "name",
        "A_value": "Ant king",
        "B_key": "type",
        "B_value": "Monster",
        "C_key": "artwork",
        "C_value": "ant-king.jpg",
        "D_key": "effect",
        "D_value": "Overwhelms an enemy monster with his ant minions",
        "E_key": "atk",
        "E_value": "1000",
        "F_key": "def",
        "F_value": "200",
        "id": "8c3c71cdfb1ebe8d14d00c49d4f11051",
    },
    {
        "A_key": "name",
        "A_value": "Warrior dude",
        "B_key": "type",
        "B_value": "Monster",
        "C_key": "artwork",
        "C_value": "warrior-dude.jpg",
        "D_key": "effect",
        "D_value": "Bashes everyone's head",
        "E_key": "atk",
        "E_value": "800",
        "F_key": "def",
        "F_value": "500",
        "id": "5819e04a9ebbceb4107d10a529806f9f",
    },
    {
        "A_key": "name",
        "A_value": "Bomberbot 9000",
        "B_key": "type",
        "B_value": "Machine",
        "C_key": "artwork",
        "C_value": "bomber.jpg",
        "D_key": "effect",
        "D_value": "Barrages the field after the end of opponent's turn, taking 2/3 monster's ATK from opponent and 1/3 from player.",
        "E_key": "atk",
        "E_value": "900",
        "F_key": "def",
        "F_value": "300",
        "G_key": "",
        "G_value": "",
        "H_key": "",
        "H_value": "",
        "I_key": "events",
        "I_value": "v1_buff_friendly, atk, 200; v1_buff_friendly, atk, 200;",
        "id": "b708a3fc5b66886f89cca197a8a78438",
    },
    {
        "A_key": "name",
        "A_value": "Light guy",
        "B_key": "",
        "B_value": "",
        "C_key": "artwork",
        "C_value": "light-guy.jpeg",
        "D_key": "effect",
        "D_value": "Increases friendly monster's ATK by 200 for the next two turns",
        "E_key": "",
        "E_value": "",
        "F_key": "",
        "F_value": "",
        "G_key": "",
        "G_value": "",
        "H_key": "",
        "H_value": "",
        "I_key": "events",
        "I_value": "v1_buff_friendly, atk, 200; v1_buff_friendly, atk, 200; v1_buff_friendly, atk, 200; ",
        "id": "90dd5dc27ed82038e3425b0fd2fd5a88",
    },
    {
        "A_key": "name",
        "A_value": "Dark guy",
        "B_key": "",
        "B_value": "",
        "C_key": "artwork",
        "C_value": "dark-guy.jpg",
        "D_key": "effect",
        "D_value": "Reduces ATK of all monsters by 200 for the next 2 turns",
        "E_key": "",
        "E_value": "",
        "F_key": "",
        "F_value": "",
        "G_key": "",
        "G_value": "",
        "H_key": "",
        "H_value": "",
        "I_key": "events",
        "I_value": "v1_debuff_friendly, atk, 200; v1_debuff_enemies, atk, 200; v1_debuff_friendly, atk, 200; v1_debuff_enemies, atk, 200; ",
        "id": "573339c12f19518afa3302e617b33e40",
    },
    {
        "A_key": "name",
        "A_value": "Insect swarm",
        "B_key": "type",
        "B_value": "plague",
        "C_key": "artwork",
        "C_value": "insect-swarm.jpg",
        "D_key": "effect",
        "D_value": "Removes one random card from enemy field",
        "E_key": "",
        "E_value": "",
        "F_key": "",
        "F_value": "",
        "G_key": "",
        "G_value": "",
        "H_key": "",
        "H_value": "",
        "I_key": "events",
        "I_value": "v1_remove_random_enemy",
        "id": "e5506b26c0b2e30c974d201d16540918",
    },
    {
        "A_key": "name",
        "A_value": "Elemental interception",
        "B_key": "type",
        "B_value": "Instant",
        "C_key": "artwork",
        "C_value": "elemental-interception.jpeg",
        "D_key": "effect",
        "D_value": "When opponent attacks you with a monster, instantly deal 500 damage to that monster",
        "E_key": "",
        "E_value": "",
        "F_key": "",
        "F_value": "",
        "G_key": "",
        "G_value": "",
        "H_key": "",
        "H_value": "",
        "I_key": "events",
        "I_value": "v1_debuff_enemy, atk, 500",
        "id": "6415ebfd81c2aa6ddf9a9be90b9caf7a",
    },
]


@controller.route("/cards", methods=["GET"])
async def list_cards():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    res = await gamedb.cards.find({}).to_list()
    secondary, tertiary = listed(cards=res)

    return await hiccpage(trident(menu(), secondary, tertiary))


@controller.route("/web/part/game/cards/<card_id>", methods=["GET"])
async def show_card(card_id: str):
    c: T.Optional[dict] = await gamedb.cards.find_one({"id": card_id})
    if c is None:
        raise Exception(f"Card {card_id} not found")

    return html(["div", {"class": "game"}, card(c)])


@controller.route("/web/part/game/cards/new", methods=["GET"])
def new_card():
    return html(creation_complexity())


@controller.route("/web/part/game/cards/new", methods=["POST"])
async def store_card():
    data: dict = request.form.to_dict()
    data["id"] = os.urandom(16).hex()

    await gamedb.cards.insert_one(data)
    return html([card(data)])


@controller.route("/web/part/game/cards/new/<level>", methods=["GET"])
def new_card_next(level: str):
    return html(creation_detailed(level))


@controller.route("/web/part/game/artwork/new", methods=["GET"])
def artwork_form():
    return _convert_tree(
        [
            "div",
            {"id": "artwork", "class": "game"},
            [
                "form",
                {
                    "hx-post": "/web/part/game/artwork/new",
                    "enctype": "multipart/form-data",
                },
                [
                    ["input", {"type": "file", "name": "artwork"}],
                    ["button", {"type": "submit", "class": "btn"}, "SEND"],
                ],
            ],
        ]
    )


@controller.route("/web/part/game/artwork/new", methods=["POST"])
def artwork_upload():
    f = request.files["artwork"]

    assert f is not None
    assert f.filename != ""
    filename = secure_filename(f.filename)
    f.save(join(current_app.config["UPLOAD_FOLDER"], filename))

    return _convert_tree(
        [
            [
                "div",
                {"class": "floater"},
                [
                    "a",
                    {
                        "class": "material-icons",
                        "href": "#",
                        "onclick": "document.querySelector('#artwork').classList.toggle('game')",
                    },
                    "close",
                ],
            ],
            ["p", {}, filename],
            ["img", {"src": f"resources/app/img/{filename}"}],
        ]
    )
