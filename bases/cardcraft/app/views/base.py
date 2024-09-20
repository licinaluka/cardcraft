from flask import url_for
from pyhiccup.core import html

from cardcraft.app.views.theme import theme
from cardcraft.app.views.navigation import menu, navigation

js = lambda e: url_for("static", filename=e)

def trident(a, b, c):
    return [
        "div",
        {"class": "millers columns"},
        [
            ["div", {"class": "column primary", "id": "menu"}, a],
            ["div", {"class": "column secondary"}, b],
            ["div", {"class": "column tertiary"}, c],
        ]
    ]


def hiccpage(page):
    return html(
        [
            [
                "head",
                [
                    "meta",
                    {
                        "content": "width=device-width, initial-scale=1",
                        "name": "viewport",
                    },
                ],
                ["meta", {"charset": "UTF-8"}],
                [
                    "link",
                    {
                        "rel": "stylesheet",
                        "href": "https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css",
                    },
                ],
                [
                    "link",
                    {
                        "rel": "stylesheet",
                        "href": "https://fonts.googleapis.com/icon?family=Material+Icons",
                    },
                ],
                ["style", {"type": "text/css"}, theme()],
            ],
            [
                "body",
                {"hx-boost": "true"},
                navigation(),
                page,
                ["script", {"src": js("app/htmx.min.js")}, " "],
                ["script", {"src": js("app/json-enc.js")}, " "],
                ["script", "htmx.config.withCredentials=true"],
                ["script", {"src": js("app/bundle.js"), "type": "module"}, " "],
            ],
        ],
        etype="html5",
        dir="ltr",
    )
