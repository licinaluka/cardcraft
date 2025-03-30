import html
import os
import typing as T

from cardcraft.game.system import Match


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
                        f"/game/resources/app/img/{d['C_value']}"
                        if d["C_value"] is not None
                        else "data:,"
                    )
                },
            ],
        ],
        ["hr"],
        ["p", d["J_value"]] if "J_value" in d else None,  # type: ignore[list-item]
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
            ["img", {"src": "/game/resources/app/img/warrior-dude.jpg"}],
        ],
        ["hr"],
        calc(":J") <= limit and ["p", ":J"],  # type: ignore[list-item]
        ["small", {"id": f"card-{identifier}", "class": "c-content"}, ":D"],
        ["hr"],
        ["p", ["b", ":E"], ["b", ":F"], calc(":G") <= limit and ["b", ":G"]],
    ]


def listed(cards: list):

    create_btn = [
        "a",
        {
            "class": "btn purple",
            "hx-get": "/game/web/part/game/cards/new",
            "hx-target": ".tertiary",
        },
        "create a card",
    ]

    return (
        [
            "div",
            [
                create_btn,
                ["span", " | "],
                [
                    "a",
                    {
                        "class": "btn purple lighten-2",
                        "hx-get": "/game/web/part/game/artwork/new",
                        "hx-target": ".tertiary",
                    },
                    "upload artwork",
                ],
                [
                    "div",
                    {"class": "collection black"},
                    [
                        [
                            "a",
                            {
                                "hx-get": f"/game/web/part/game/cards/{e['id']}",
                                "hx-target": ".tertiary",
                                "class": "collection-item avatar",
                            },
                            [
                                "img",
                                {
                                    "src": f"/game/resources/app/img/{e['C_value']}",
                                    "class": "circle",
                                },
                            ],
                            ["span", {"class": "title"}, e["A_value"]],
                            ["p", e["D_value"]],
                        ]
                        for e in cards  # type: ignore[list-item]
                    ]
                    or ["p", "No cards found"],  # type: ignore[list-item]
                ],
            ],
        ],
        ["p", "No card selected!"],
    )


def creation_complexity():
    return [
        "div",
        {"class": "game"},
        [
            ["h4", "Card builder"],
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
                                "hx-get": f"/game/web/part/game/cards/new/{chr(e)}",
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


def creation_detailed(level: str):
    """detailed inputs for card details

    @todo split the card API table out
    """
    return [
        ["p", "Enter card details:"],
        card_complexity(f":{level}"),
        [
            "form",
            {
                "class": "card-meta",
                "hx-post": "/game/web/part/game/cards/new",
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
                                        for ln in getattr(Match, fn).__doc__.split("\n")
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
