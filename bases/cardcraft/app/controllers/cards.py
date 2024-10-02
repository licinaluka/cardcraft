import os
import typing as T

from flask import Blueprint, request
from pyhiccup.core import html

from cardcraft.app.services.db import gamedb
from cardcraft.app.services.game import Match
from cardcraft.app.views.base import hiccpage, trident
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


def card(data: dict) -> list[T.Union[str, dict, list]]:
    d: dict = data
    identifier: str = d.get("id", None) or os.urandom(16).hex()

    check = lambda e: f"{e}_value" in d and d.get(f"{e}_value", None)
    val = lambda e: d.get(f"{e}_value", None)

    def stats():
        vals = []

        if check("E") and check("F"):
            vals.append(["b", val("E")])
            vals.append(["i", "/"])
            vals.append(["b", val("F")])

        if check("G"):
            vals.append(["i", "/"])
            vals.append(["b", val("G")])

        if 1 > len(vals):
            return ["span", ""]

        return [
            ["hr"],
            ["p", vals],
        ]

    return [
        "a",
        {
            "id": f"card-{identifier}",
            "onclick": "this.classList.toggle('movable')",
            "class": "card-render",
            "draggable": True,
            "ondragstart": "(e=>e.dataTransfer.setData('text', e.target.id))(event)",
        },
        [
            "div",
            {"class": "c-image"},
            ["input", {"type": "hidden", "name": "card", "value": identifier}],
            ["p", val("H")] if check("H") else None,
            ["div", {"class": "c-title"}, d["A_value"]],
            ["p", val("B")] if check("B") else None,
            # ["p", val("I")] if check("I") else None,
            [
                "img",
                {
                    "src": (
                        f"/resources/app/img/{d['C_value']}"
                        if d["C_value"] is not None
                        else "data:,"
                    )
                },
            ],
        ],
        ["hr"],
        ["p", d["J_value"]] if "J_value" in d else None, # type: ignore[list-item]
        [
            "small",
            {"class": "c-content"},
            d["D_value"],
        ],
        stats(),
    ]


def card_complexity(level: str) -> list[T.Union[str, dict, list]]:
    identifier: str = os.urandom(16).hex()
    calc = lambda e: ord(e.strip(":"))

    limit = calc(level)
    return [
        "div",
        {"href": f"#card-{identifier}", "class": "card-render"},
        [
            "div",
            {"class": "c-image"},
            calc(":H") <= limit and ["p", ":H"],
            ["div", {"class": "c-title"}, ":A"],
            ["p", ":B"],
            calc(":I") <= limit and ["p", ":I"],
            ["p", ":C (artwork)"],
            ["img", {"src": "/resources/app/img/warrior-dude.jpg"}],
        ],
        ["hr"],
        calc(":J") <= limit and ["p", ":J"], # type: ignore[list-item]
        ["small", {"id": f"card-{identifier}", "class": "c-content"}, ":D"],
        ["hr"],
        ["p", ["b", ":E"], ["b", ":F"], calc(":G") <= limit and ["b", ":G"]],
    ]


@controller.route("/cards", methods=["GET"])
async def list_cards():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)

    assert sess_id is not None

    res = await gamedb.cards.find({}).to_list()

    create_btn = [
        "a",
        {
            "class": "btn purple",
            "hx-get": "/web/part/game/cards/new",
            "hx-target": ".tertiary",
        },
        "create a card",
    ]

    return await hiccpage(
        trident(
            menu(),
            [
                "div",
                [
                    create_btn,
                    [
                        "div",
                        {"class": "collection black"},
                        [
                            [
                                "a",
                                {
                                    "hx-get": f"/web/part/game/cards/{e['id']}",
                                    "hx-target": ".tertiary",
                                    "class": "collection-item avatar",
                                },
                                [
                                    "img",
                                    {
                                        "src": f"/resources/app/img/{e['C_value']}",
                                        "class": "circle",
                                    },
                                ],
                                ["span", {"class": "title"}, e["A_value"]],
                                ["p", e["D_value"]],
                            ]
                            for e in res
                        ]
                        or ["p", "No cards found"],
                    ],
                ],
            ],
            ["p", "No card selected!"],
        )
    )


@controller.route("/web/part/game/cards/<card_id>", methods=["GET"])
async def show_card(card_id: str):
    c: T.Optional[dict] = await gamedb.cards.find_one({"id": card_id})
    if c is None:
        raise Exception(f"Card {card_id} not found")

    return html(["div", {"class": "game"}, card(c)])


@controller.route("/web/part/game/cards/new", methods=["GET"])
def new_card():
    return html(
        [
            "div",
            {"class": "game"},
            [
                ["h3", "Card builder"],
                [
                    "p",
                    "Select a layout/complexity (note, field I is for card API functions):",
                ],
                [
                    "div",
                    {"class": "layouts"},
                    [
                        [
                            "label",
                            [
                                "a",
                                {
                                    "hx-get": f"/web/part/game/cards/new/{chr(e)}",
                                    "hx-target": ".game",
                                },
                            ],
                            [
                                "div",
                                [
                                    ["span", "Layout 1"],
                                    card_complexity(f":{chr(e)}"),
                                ],
                            ],
                        ]
                        for e in range(ord("F"), ord("K"))
                    ],
                ],
            ],
        ]
    )


@controller.route("/web/part/game/cards/new", methods=["POST"])
async def store_card():
    data: dict = request.form.to_dict()
    data["id"] = os.urandom(16).hex()

    await gamedb.cards.insert_one(data)
    return html([card(data)])


@controller.route("/web/part/game/cards/new/<level>", methods=["GET"])
def new_card_next(level: str):
    return html(
        [
            ["p", "Enter card details:"],
            card_complexity(f":{level}"),
            [
                "form",
                {
                    "class": "card-meta",
                    "hx-post": "/web/part/game/cards/new",
                    "hx-target": ".game",
                },
                [
                    [
                        [
                            [
                                "input",
                                {
                                    "type": "text",
                                    "name": f"{chr(e)}_key",
                                    "placeholder": (
                                        f"{chr(e)} key" if chr(e) != "C" else "artwork"
                                    ),
                                },
                            ],
                            [
                                "input",
                                {
                                    "type": "text",
                                    "name": f"{chr(e)}_value",
                                    "placeholder": f"{chr(e)} value",
                                },
                            ],
                        ]
                        for e in range(ord("A"), ord(level) + 1)
                    ],
                    ["button", {"type": "submit"}, "Save"],
                ],
            ],
            [
                ["h4", "Card effect API (for field 'I'):"],
                [
                    "table",
                    {"class": "responsive-table striped"},
                    [
                        ["thead", ["tr", ["th", "function"], ["th", "description"]]],
                        [
                            "tbody",
                            [
                                [
                                    "tr",
                                    ["td", fn],
                                    [
                                        "td",
                                        [
                                            ["p", ln or "&nbsp;"]
                                            for ln in getattr(Match, fn).__doc__.split(
                                                "\n"
                                            )
                                        ],
                                    ],
                                ]
                                for fn in dir(Match)
                                if fn.startswith("v1_")
                            ],
                        ],
                    ],
                ],
            ],
        ]
    )
