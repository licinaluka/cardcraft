import typing as T

from cardcraft.app.views.cards import card
from cardcraft.game.system import Match, Target

Node = T.Union[str, dict, list]


def listed(matches: list) -> list[Node]:
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

    return [
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
                                "src": f"/resources/app/img/match.jpeg",
                                "class": "circle",
                            },
                        ],
                        ["span", {"class": "title"}, e["id"]],
                    ]
                    for e in matches
                ]
                or no_matches,
            ],
        ],
    ]


def create_match_deck_selection(
    decks: list[dict], match_secret: str, addr: str, pot_fee: int
):
    return [
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
                                        "value": deck["id"],  # type: ignore[list-item]
                                    },
                                    deck["name"],
                                ],
                            ],
                        ]
                        for deck in decks  # type: ignore[list-item]
                    ],
                ],
                [
                    "input",
                    {"type": "hidden", "name": "csrf", "value": match_secret},
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
                                "min": pot_fee,
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
                        "onclick": f"window.purse.pot('{addr}', document.querySelector('#pot-lamports').value)",
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


def shown(game: Match, identity, pot_status, deck, pl, hand, op, ophand) -> Node:
    return [
        [
            "div",
            {"class": "game", "id": "game"},
            [
                ["div", {"id": "loading", "class": "shown"}, " "],
                [
                    "a",
                    {
                        "class": "btn purple game-refresh-trigger",
                        "hx-get": f"/web/part/game/matches/{game.id}",
                        "hx-target": ".tertiary",
                        "hx-trigger": "click, every 9s",
                    },
                    "Refresh",
                ],
                ["span", " | "],
                (
                    [
                        "a",
                        {
                            "class": "btn red",
                            "hx-post": f"/web/part/game/matches/{game.id}/do",
                            "hx-vals": "js:{"
                            + f"event: ['{identity}', 'end_turn', null]"
                            + "}",
                            "hx-ext": "json-enc",
                            "hx-trigger": "click",
                            "hx-swap": "none",
                        },
                        "End turn",
                    ]
                    if game.get("is_turn", Target.Player, identity)
                    else (
                        ["small", "Opponent turn"]
                        if game.winner is None
                        else ["small", f"{game.winner} WON"]
                    )
                ),
                ["span", " | "],
                [
                    "p",
                    {"class": "btn grey"},
                    pot_status,
                ],
                (
                    ["p", {"class": "btn blue lighten-2"}, "PASS"]
                    if game.get("can_respond", Target.Player, identity)
                    else ["small", "/"]
                ),
                [
                    "div",
                    {"class": "board"},
                    [
                        "div",
                        {"class": "opponent"},
                        [
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
                                                "C_value": "card-unknown.jpeg",
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
                            [
                                "div",
                                {"id": f"unit-bot1"},
                                [
                                    "div",
                                    {
                                        "class": "spot",
                                        "style": "width:7em;height:14em;",
                                        "ondrop": "drop(event)",
                                        "ondragover": "allowDrop(event)",
                                        "onclick": "move(event)",
                                    },
                                    card(
                                        {
                                            "id": "something",
                                            "A_value": op["name"],
                                            "C_value": "bot1.jpeg",
                                            "D_value": "Pro card player, trained specifically to challenge you",
                                        }
                                    ),
                                    ["small", f"{op['hp']}/{op['hpmax']}"],
                                    ["p", op["name"]],
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
                                                            i < (len(game.fields) / 2)
                                                            and j < (len(field))
                                                        )
                                                        else ""
                                                    ),
                                                    "ondrop": "drop(event)",
                                                    "ondragover": "allowDrop(event)",
                                                    "onclick": "move(event)",
                                                },
                                                (
                                                    card(game.fields[i][j] or {})
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
                                                "hx-post": f"/web/part/game/matches/{game.id}/do",
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
                                else ["p", "No cards left in deck"]  # type: ignore[list-item]
                            ),
                        ],
                    ],
                ],
            ],
        ]
    ]
