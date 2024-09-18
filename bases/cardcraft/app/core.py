import base58
import json
import hashlib
import hmac
import os
import random
import time
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


def menu():
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
            ["li", ["a", {"href": "/"}, "home"]],
            ["li", ["a", {"href": "/web/thing" + "/research"}, "thing"]],
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
                menu(),
                [
                    "div",
                    {"class": "millers columns"},
                    [
                        ["div", {"class": "column primary"}, "ok"],
                        [
                            "div",
                            {"class": "column secondary"},
                            [["p", {}, f"game {e}"] for e in range(1, 20)],
                        ],
                        ["div", {"class": "column tertiary"}, "lorem ipsum"],
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
