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


async def hiccpage(page):
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
                await navigation(),
                page,
                ["script", {"src": js("app/htmx.min.js")}, " "],
                ["script", {"src": js("app/json-enc.js")}, " "],
                ["script", "htmx.config.withCredentials=true"],
                ["script", {"src": js("app/bundle.js"), "type": "module"}, " "],
                ["script", """
                    async function drop(e) {
                        e.preventDefault()
                        let id = e.dataTransfer.getData('text')
                        let card_id = id.replace('card-', '')

                        let el = document.querySelector('#' + id)
                        e.target.appendChild(el)

                        await fetch(
                            `/web/part/game/matches/current/do`,
                            {
                                method: 'POST',
                                credentials: 'include',
                                body: JSON.stringify({'event': ['identity', 'play', `h-${card_id}, ${e.target.parentNode.id}`]}),
                                headers: {'Content-Type': 'application/json'}
                            }
                        )
                    }

                    function allowDrop(e) {
                        e.preventDefault()
                    }                
                """]
            ],
        ],
        etype="html5",
        dir="ltr",
    )
