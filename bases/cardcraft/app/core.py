import base58
import json
import hashlib
import hmac
import multiprocessing
import os
import random
import signal
import sys
import time
import typing as T
import uuid

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, Response, redirect, request, url_for
from nacl.signing import VerifyKey
from pyhiccup.core import _convert_tree, html
from solders.pubkey import Pubkey
from types import SimpleNamespace

from cardcraft.app.controllers.cards import card, controller as cards
from cardcraft.app.controllers.decks import controller as decks
from cardcraft.app.controllers.matches import controller as matches
from cardcraft.app.services.db import gamedb
from cardcraft.app.services.engine import loop
from cardcraft.app.services.mem import mem
from cardcraft.app.views.base import hiccpage, trident
from cardcraft.app.views.navigation import menu
from cardcraft.app.views.theme import theme

app = Flask(__name__, static_url_path="/resources", static_folder="./resources")
app.register_blueprint(cards)
app.register_blueprint(decks)
app.register_blueprint(matches)

lock = multiprocessing.Lock()
p = multiprocessing.Process(target=loop, args=(lock,))
p.start()

def reloaded(*a):
    p.terminate()
    p.join()
    sys.exit()


signal.signal(signal.SIGINT, reloaded)

# @app.errorhandler(Exception)
def exceptions(err):
    resp = Response(
        json.dumps({"detail": str(err)}), status=500, mimetype="application/json"
    )
    return resp


@app.route("/")
async def landing():
    return await hiccpage(
        trident(
            menu(),
            ["span", {"hx-get": "/web/part/game/matches", "hx-trigger": "load"}, " "],
            [
                "div",
                {"style": "padding:2em;"},
                "Select a previous match or start a new one",
            ],
        )
    )


@app.route("/api/part/game/authn", methods=["POST"])
async def authn():
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

    await gamedb.sessions.update_one(
        {"ref": "ref"},
        {"$set": mem["session"][ref]},
        upsert=True,
    )

    resp = Response()
    resp.code = 204
    return resp


@app.route("/api/part/game/authn/challenge", methods=["POST"])
async def challenge():
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
        "ref": ref,
        "nonce": nonce,
        "key": key,
        "cid": cid,
        "challenge": challenge,
    }

    resp = Response(
        json.dumps({"cid": cid, "message": challenge}),
        headers={
            "Set-Cookie": f"ccraft_sess={ref}; Path=/",
            "Content-type": "application/json",
        },
    )

    return resp


asgi_app = WsgiToAsgi(app)
