import base58
import json
import hashlib
import hmac
import os
import random
import time
import typing as T
import uuid

from flask import Flask, Response, request, url_for
from nacl.signing import VerifyKey
from pyhiccup.core import _convert_tree, html
from solders.pubkey import Pubkey
from types import SimpleNamespace

from cardcraft.app.theme import theme

app = Flask(__name__, static_url_path="/resources", static_folder="./resources")

js = lambda e: url_for("static", filename=e)

mem: dict = {"session": {}, "cid": 1}


# @app.errorhandler(Exception)
def exceptions(err):
    resp = Response(
        json.dumps({"detail": str(err)}), status=500, mimetype="application/json"
    )
    return resp


@app.route("/")
def landing():
    return hiccpage()


@app.route("/api/part/game/authn", methods=["POST"])
def authn():
    cid: int = request.json.get("challenge")
    nonce: str = request.json.get("nonce")
    signature: str = request.json.get("signature")

    ref: T.Optional[str] = request.cookies.get("ccraft_sess")

    assert ref is not None
    assert ref in mem["session"]

    assert mem["session"][ref]["key"] is not None
    assert cid == mem["session"][ref]["cid"], json.dumps(mem["session"][ref])

    session: dict = mem["session"][ref]

    pubkey_b: bytes = bytes(Pubkey.from_string(session["key"]))
    challenge_b: bytes = bytes(session["challenge"], "utf-8")
    signature_b: bytes = bytes(signature, "utf-8")

    VerifyKey(pubkey_b).verify(
        base58.b58decode(challenge_b), base58.b58decode(signature_b)
    )

    mem["session"][ref]["verification"] = int(time.time())

    resp = Response()
    resp.code = 204
    return resp


@app.route("/api/part/game/authn/challenge", methods=["POST"])
def challenge():
    ref: T.Optional[str] = request.cookies.get("ccraft_sess")

    session = SimpleNamespace()
    session.asserted: bool = ref is not None
    session.exists: bool = ref in mem["session"]
    session.is_valid: bool = (int(time.time()) - 3600) < mem["session"].get(
        ref, {}
    ).get("verification_time", int(time.time()))

    if session.asserted and session.exists and session.is_valid:
        return Response(json.dumps({"detail": "Already logged in"}), status=302)

    key: str = request.json.get("key")
    nonce: str = request.json.get("nonce")

    ref: str = str(uuid.uuid4())
    cid: int = mem["cid"]

    guid: str = str(uuid.uuid4())
    challenge = base58.b58encode(
        bytes(f"cardcraft-authn-challenge-{guid}", "utf-8")
    ).decode("utf-8")

    mem["cid"] = mem["cid"] + 1

    mem["session"][ref] = {
        "nonce": nonce,
        "key": key,
        "cid": cid,
        "challenge": challenge,
    }

    resp = Response(
        json.dumps({"cid": cid, "message": challenge}),
        headers={
            "Set-Cookie": f"ccraft_sess={ref}",
            "Content-type": "application/json",
        },
    )

    return resp


@app.route("/web/part/game/identity")
def identity():
    return []


def card(data: dict) -> list[T.Union[str, dict, list]]:
    d: dict = data
    identifier: str = os.urandom(16).hex()
    return [
        "a",
        {
            "href": f"#c-content-{identifier}",
            "class": "card-render"
        },
        [
            "div",
            {"class": "c-image"},
            ["div", {"class": "c-title"}, d["name"]],
            ["img", {"src": d["artwork"]}],
        ],
        ["small", {"id": f"c-content-{identifier}", "class": "c-content"}, d["effect"]],
    ]


@app.route("/web/part/game/match/new", methods=["GET"])
def new_match():
    hand: list[dict] = [
        {
            "name": "Awakening of the Possessed",
            "cardType": "Spell",
            "property": "Continuous",
            "password": "62256492",
            "effect": 'Monsters you control gain 300 ATK for each different Attribute you control. "Charmer" and "Familiar-Possessed" monsters you control cannot be destroyed by card effects. If a Spellcaster monster(s) with 1850 original ATK is Normal or Special Summoned to your field: Draw 1 card. You can only use this effect of "Awakening of the Possessed" once per turn.',
            "cardSet": [
                {
                    "releasedDate": "2020-03-19",
                    "code": "DUOV-EN030",
                    "name": "Duel Overload",
                    "rarity": "Ultra Rare",
                },
                {
                    "releasedDate": "2020-10-22",
                    "code": "SDCH-EN020",
                    "name": "Structure Deck: Spirit Charmers",
                    "rarity": "Common",
                },
            ],
            "artwork": "https://yugicrawler.vercel.app/artwork/62256492",
        },
        {
            "name": "Dark Magician",
            "cardType": "Monster",
            "atk": "2500",
            "def": "2100",
            "monsterTypes": "Spellcaster / Normal",
            "attribute": "DARK",
            "isToken": False,
            "level": "7",
            "password": "36996508",
            "limitation_text": "",
            "effect": "The ultimate wizard in terms of attack and defense.",
            "cardSet": [
                {
                    "releasedDate": "2015-11-12",
                    "code": "YGLD-ENB02",
                    "name": "Yugi's Legendary Decks",
                    "rarity": "Ultra Rare",
                },
                {
                    "releasedDate": "2023-08-24",
                    "code": "SBC1-ENG01",
                    "name": "Speed Duel: Streets of Battle City",
                    "rarity": "Secret Rare",
                },
                {
                    "releasedDate": "2023-08-24",
                    "code": "SBC1-ENG10",
                    "name": "Speed Duel: Streets of Battle City",
                    "rarity": "Common",
                },
            ],
            "artwork": "https://yugicrawler.vercel.app/artwork/36996508",
        },
    ]

    return html(
        [
            "div",
            {"class": "game"},
            [
                "div",
                {"class": "board"},
                [
                    "div",
                    {"class": "opponent"},
                    [
                        ["p", "OP"],
                        ["div", {"class": "hand"}, [card({
                            "name": "?",
                            "effect": "?",
                            "artwork": "https://upload.wikimedia.org/wikipedia/en/2/2b/Yugioh_Card_Back.jpg"
                        }) for e in range(1, random.randint(1, 7))]]
                    ]
                ],
                ["p", {"class": "battle", "id": "battle"}, "BAT"],
                [
                    "div",
                    {"class": "player"},
                    [
                        ["p", "PL"],
                        ["div", {"class": "hand"}, [card(e) for e in hand]],
                    ],
                ],
            ],
        ]
    )


def navigation():
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
            ["li", ["a", {"href": "#menu", "style":"transform: rotate(90deg);"}, "|||"]],
            ["li", ["a", {"href": "/"}, "home"]],
            ["li", ["a", {
                "hx-get": "/web/part/game/match/new",
                "hx-target": ".tertiary",
                "hx-swap": "innerHTML",
                "class": "btn purple"
            }, "New game"]],
            [
                "li",
                {"class": "right"},
                [
                    "a",
                    {
                        "onclick": "window.purse.connect()",
                        "title": "connect a wallet",
                    },
                    "o/ (connect)",
                ],
            ],
        ],
    ]


def games():
    matches = []
    if 0 < len(matches):
        return [["p", {}, f"game {e}"] for e in matches]

    return [
        "div",
        {
            "class": "no-matches"
        },
        [
            [
                "div",
                {"style": "color: #888; cursor: default; user-select: none"},
                "No previous games!",
            ],
            ["br"],
            [
                "a",
                {
                    "hx-get": "/web/part/game/match/new",
                    "hx-target": ".tertiary",
                    "hx-swap": "innerHTML",
                    "class": "purple-text",
                },
                " ... start one!",
            ],
        ],
    ]


def menu():
    return ["div", ["ul", [["li", ["a", {}, "Games"]], ["li", ["a", {}, "Decks"]]]]]

def hiccpage():
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
                navigation(),
                [
                    "div",
                    {"class": "millers columns"},
                    [
                        ["div", {"class": "column primary", "id": "menu"}, menu()],
                        ["div", {"class": "column secondary"}, games()],
                        [
                            "div",
                            {"class": "column tertiary"},
                            ["div", {"style": "padding:2em;"}, "Select a previous match or start a new one"],
                        ],
                    ],
                    ["script", {"src": js("app/htmx.min.js")}, " "],
                    ["script", {"src": js("app/json-enc.js")}, " "],
                    ["script", {"src": js("app/bundle.js"), "type": "module"}, " "],
                ],
            ],
        ],
        etype="html5",
        **{"dir": "ltr"},
    )
