import typing as T

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
                                "src": f"/resources/app/img/card-back-ue-pirated.jpg",
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

def shown(match: dict) -> Node:
    return []