import typing as T

from cardcraft.app.views.cards import card


def listed(decks: list[dict]):
    return [
        [
            "a",
            {
                "class": "btn purple",
                "hx-get": "/web/part/game/decks/new",
                "hx-target": ".tertiary",
            },
            "create a deck",
        ],
        [
            "ul",
            {"class": "collection"},
            [
                [
                    "li",
                    {"class": "collection-item avatar"},
                    [
                        [
                            "img",
                            {
                                "class": "circle",
                                "src": "/resources/app/img/card-back.jpeg",
                            },
                            " ",
                        ],
                        [
                            "a",
                            {
                                "class": "title",
                                "hx-get": f"/web/part/game/decks/{e['id']}",
                                "hx-target": ".tertiary",
                            },
                            e["name"],
                        ],
                        ["p", ["small", f"{len(e['cards'])} in deck"]],
                    ],
                ]
                for e in decks
            ],
        ],
    ]


def shown(deck: dict, available: list[dict], used: list[dict]):

    available_view: list = [card(e) for e in available] or [
        "p",
        "No unused cards availble",
    ]
    used_view: list = [card(e) for e in used] or ["p", "Put cards here"]

    return [
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
                        "hx-put": f"/web/part/game/decks/{deck['id']}",
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


def create_deck(cards: list[dict]):
    return [
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
                        [card(e) for e in cards],
                    ],
                ],
            ],
        ],
    ]
