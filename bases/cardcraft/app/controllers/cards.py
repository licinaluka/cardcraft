import os
import typing as T

from flask import Blueprint, request
from pyhiccup.core import html

from cardcraft.app.mem import mem
from cardcraft.app.views.base import hiccpage, trident
from cardcraft.app.views.navigation import menu, navigation
from cardcraft.app.services.db import gamedb

controller = Blueprint("cards", __name__)

demo = [
    {
        "id": "abc123",
        "A_value": "Warrior dude",
        "C_value": "warrior-dude.jpg",
        "D_value": "Beats everyone over the head",
        "E_value": "300",
        "F_value": "300",
    },
    {
        "id": "abc124",
        "A_value": "Light guy",
        "C_value": "light-guy.jpeg",
        "D_value": "Increases friendly monsters' HP by 200",
    },
    {
        "id": "abc125",
        "A_value": "Dark guy",
        "C_value": "dark-guy.jpg",
        "D_value": "Reduces HP of all monsters on the field by 200",
    },
    {
        "id": "abc126",
        "A_value": "Insect swarm",
        "B_value": "plague",
        "C_value": "insect-swarm.jpg",
        "D_value": "Removes all but one card from enemy field",
    },
]

if 1 > len(mem["cards"]):
    mem["cards"] += demo


def card(data: dict) -> list[T.Union[str, dict, list]]:
    d: dict = data
    identifier: str = d.get("id", None) or os.urandom(16).hex()

    check = lambda e: f"{e}_value" in d
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
            "href": f"#card-{identifier}",
            "class": "card-render",
            "draggable": True,
            "ondragstart": "(e=>e.dataTransfer.setData('text', e.target.id))(event)"
        },
        [
            "div",
            {"class": "c-image"},
            ["input", {"type": "hidden", "name": "card", "value": identifier}],
            ["div", {"class": "c-title"}, d["A_value"]],
            ["p", val("B")] if check("B") else None,
            ["p", val("H")] if check("H") else None,
            ["p", val("I")] if check("I") else None,
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
        ["p", d["J_value"]] if "J_value" in d else None,
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
            ["div", {"class": "c-title"}, ":A"],
            ["p", ":B"],
            calc(":H") <= limit and ["p", ":H"],
            calc(":I") <= limit and ["p", ":I"],
            ["p", ":C (artwork)"],
            ["img", {"src": "/resources/app/img/warrior-dude.jpg"}],
        ],
        ["hr"],
        calc(":J") <= limit and ["p", ":J"],
        ["small", {"id": f"card-{identifier}", "class": "c-content"}, ":D"],
        ["hr"],
        ["p", ["b", ":E"], ["b", ":F"], calc(":G") <= limit and ["b", ":G"]],
    ]


@controller.route("/cards", methods=["GET"])
async def list_cards():
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

    return hiccpage(
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


@controller.route("/web/part/game/cards/<id>", methods=["GET"])
def show_card(id: str):
    c: T.Optional[dict] = next(filter(lambda e: e["id"] == id, mem["cards"]), None)
    if c is None:
        raise Exception(f"Card {id} not found!")

    return html(["div", {"class": "game"}, card(c)])


@controller.route("/web/part/game/cards/new", methods=["GET"])
def new_card():
    return html(
        [
            "div",
            {"class": "game"},
            [
                ["p", "Select a layout/complexity:"],
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

    # key: T.Optional[str] = None

    # for k, v in request.form.to_dict().items():
    #     _, node = k.split("_")
    #     if node == "key":
    #         key = v

    #     if node == "value":
    #         data[key] = v

    mem["cards"].append(data)
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
        ]
    )
