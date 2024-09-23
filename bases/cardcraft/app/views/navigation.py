import typing as T

from flask import request
from cardcraft.app.services.db import gamedb
from cardcraft.app.services.mem import mem

def menu():
    return ["div",
      ["ul", [
        ["li", ["a", {}, "Games"]],
        ["li", ["a", {"href": "/decks"}, "Decks"]],
        ["li", ["a", {"href": "/cards"}, "Cards"]]]]]



async def navigation():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess")

    if sess_id is not None:
        session = await gamedb.sessions.find_one({"ref": sess_id})
        if session is not None and sess_id not in mem["session"]:
            mem["session"][sess_id] = session

    authenticated: bool = sess_id is not None and sess_id in mem["session"]
    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)

    sign_in = [
        "a",
        {
            "id": "connection",
            "onclick": "window.purse.connect()",
        },
        identity or "connect o/"
    ]

    return [
        "nav",
        {"class": "nav-wrapper purple white-text darken-3"},
        [
            "ul",
            [
                "li",
                {"onclick": "contexts()", "style": "background:blue;cursor:pointer"},
                ["i", {"class": "material-icons insert_chart"}, " "],
            ],
            ["li", ["a", {"onclick": "document.querySelector('#menu').style.display = document.querySelector('#menu').style.display == 'block' ? 'none': 'block'", "style":"transform: rotate(90deg);"}, "|||"]],
            ["li", ["a", {"href": "/"}, "home"]],
            # ["li", ["a", {
            #     "hx-post": "/web/part/game/match/new",
            #     "hx-target": ".tertiary",
            #     "hx-swap": "innerHTML",
            #     "class": "btn purple"
            # }, "New game"]],
            [
                "li",
                {"class": "right"},
                sign_in if not authenticated else ["a", identity]
            ],
        ],
    ]
