import base58
import json
import hashlib
import hmac
import multiprocessing
import os
import random
import re
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
from cardcraft.app.views.navigation import menu, navigation
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
    if request.cookies.get("ccraft_sess") is not None:
        return redirect("/home")

    return _convert_tree(
        [
            [
                "head",
                ["title", "Cardcraft, the Solana TCG builder"],
                [
                    "link",
                    {
                        "rel": "stylesheet",
                        "href": "https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css",
                    },
                ],
                [
                    "style",
                    """
                body {
                    background-color: #000;
                    color: #fff;
                }
                a {
                    color: #9b59b6;
                }
                """,
                ],
            ],
            [
                "body",
                [
                    [
                        "pre",
                        {"style": "white-space:break-spaces;"},
                        [
                            [
                                "span",
                                """
    # Project Leo

    cardcraft as a working title.

    A white-label Solana trading card game builder as a service (TCGBaaS) platform that helps trading card game designers on Solana solve - at least - problems of

    - game implementation details
    - content customization
    - gameplay customization
    - software development and distribution

    Why this project?

    Because if making a highly customizable card game engine was simple or easy, everyone would do it.
    But it's not simple, or easy, unless you have some tricks up your sleeve.

    """,
                            ],
                            [
                                "a",
                                {"href": "/home", "class": "btn purple"},
                                "Get started",
                            ],
                            [
                                "span",
                                """
    ---
    ## Project roadmap

    ### Eparistera Daimones

    Done so far (Oct 1st 2024):
        - wallet auth
        - highly customizable, human readable, card creation system
        - a human readable card API system
        - deck building
        - match listing & starting
        - match pot & payout
        - match pot can be funded by bot/system (play to earn)
        - a (very) basic opponent bot
        - minimal game *engine*
        - highly customizable game *rule system*
        - deployment automation

    ### The Starway Eternal

    Currently doing (TBA):
        - game engine features present in most card games

    ### Endorama

    Next steps (TBA):
        - playtest automation
        - match browser, match lobbies, tournaments
        - leaderboards and ranking systems
        - card ownership
        - card trading and renting

    ### Récidive

    Future steps:
        - multiple different white-label game clients (desktop/mobile etc)
        - match betting
        - authenticity/nonce verification for real, printed cards
        - producing real, printed cards

    """,
                            ],
                        ],
                    ]
                ],
            ],
        ]
    )


@app.route("/home", methods=["GET"])
async def home():
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


@app.route("/help", methods=["GET"])
async def help():
    faq = {
        "What is this project?": "A white-label Solana trading card game builder. This instance (at https://cardcraft.ix.tc) is a demo.",
        "How do I use the demo?": "Create cards in the <a class='purple-text lighten-2' href='/cards'>card creator</a>, add them to your decks in the <a class='purple-text lighten-2' href='/decks'>deck builder</a>, then <a class='purple-text lighten-2' href='/home'>play a match</a> using one of your decks",
        "What is a white-label Solana trading card game builder?": "A turnkey software solution that helps you build a highly custom trading card game you've always been wanting to build.",
        "What are the key features of this project?": "At the moment, wallet sign in, flexible card creation, a deck builder, playing a match for SOL and a rudimentary game engine, game screen, and opponent bot.",
        "How can I make my own game?": "Install via ssh: <br /><pre>ssh you@yourvps.com -f 'wget https://raw.githubusercontent.com/licinaluka/cardcraft/refs/heads/master/config/deploy.sh | sh -'</pre>",
        "Why use this instead of programming my own?": "The overhead. <br /> <br /> In a scenario where you want to make a game but let someone else worry about the software, while we want to write the software and let someone else worry about game balancing and worldbuilding, we have a win-win situation.",
        "What types of card games can be built using this?": "The secret ingredient in this project is a highly flexible rule engine, card events we can support are basically limitless. Current game engine - though - is limited to 1 on 1 gameplay without a resource system.",
        "What kind of customization options are available for game creators?": "For MVP, you can configure bot pot behavior, pot payouts. First steps towards customizing look and feel for the web version will be in the form of minimal CMS functionality with a few pre-installed theme variations into which you can put your own branding.",
        "What kind of support is available for creators?": "We will provide automatic updates in an approach similar to the installation script, and prioritized custom patches on demand. We will also assist and advise programmers on implementing their own features.",
        "What are the pricing and licensing plans?": "TBA",
        "What is the roadmap for development?": "<ul><li>'The Starway Eternal' (TBA)</li><p>implementing features present in most card games; <li>'Endorama' (TBA)</li> <p>playtest automation, match browser, lobbies, tournaments, leadership, ranking system, card ownership, trading and renting;</p> <li>Récidive (TBA) </li> <p>multiple game clients, match betting, nonce verification for real, printed cards</p></ul>",
        "Any plans to integrate with other Solana projects": "TBA",
        "Any plans to integrate with other non-blockchain and blockchain software?": "TBA",
        "What are the plans for monetization and revenue generation?": "TBA",
        "What separates this project from other similar projects?": "The secret ingredient, the flexible rule engine.",
    }

    slug = lambda e: re.sub(r"[\W_]+", "-", e).lower().strip("-")

    return await hiccpage(
        trident(
            menu(),
            [
                "ul",
                {"class": "collection"},
                [
                    [
                        "li",
                        {"class": "collection-item"},
                        [
                            "a",
                            {
                                "href": f"#{slug(q)}",
                                "onclick": "document.querySelector('#faq').classList.toggle('game')",
                            },
                            f"{i+1}. {q}",
                        ],
                    ]
                    for i, (q, a) in enumerate(faq.items())
                ],
            ],
            [
                [
                    "div",
                    {"class": "floater"},
                    [
                        "a",
                        {
                            "class": "material-icons",
                            "href": "#",
                            "onclick": "document.querySelector('#faq').classList.toggle('game')",
                        },
                        "close",
                    ],
                ],
                [
                    "div",
                    {"id": "faq", "class": ""},
                    [
                        [
                            [
                                ["h5", {"id": slug(q)}, ["a", {"href": f"#{slug(q)}"}, f"{i+1}. {q}"]],
                                ["p", a],
                                ["br"]
                            ]
                            for i, (q, a) in enumerate(faq.items())
                        ]
                    ],
                ],
            ],
        )
    )


@app.route("/api/part/game/authn", methods=["POST"])
async def authn():
    body: T.Optional[dict] = request.json

    if body is None:
        raise Exception("No data sent!")

    cid: T.Optional[int] = body.get("challenge")

    if cid is None:
        raise Exception("Challenge is missing!")

    nonce: T.Optional[str] = body.get("nonce")

    if nonce is None:
        raise Exception("Nonce is missing!")

    signature: T.Optional[str] = body.get("signature")

    if signature is None:
        raise Exception("Signature is missing!")

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

    resp = Response(status=204)
    return resp


@app.route("/api/part/game/authn/logout", methods=["GET"])
async def logout():
    return Response(
        status=303,
        headers={"Set-Cookie": f"ccraft_sess=nil;path=/;max-age=1", "Location": "/"},
    )


@app.route("/api/part/game/authn/challenge", methods=["POST"])
async def challenge():
    ref: T.Optional[str] = request.cookies.get("ccraft_sess")

    session = SimpleNamespace(
        asserted=ref is not None,
        exists=ref in mem["session"],
        is_valid=(int(time.time()) - 3600)
        < mem["session"].get(ref, {}).get("verification_time", int(time.time())),
    )

    if session.asserted and session.exists and session.is_valid:
        return Response(json.dumps({"detail": "Already logged in"}), status=302)

    body: T.Optional[dict] = request.json

    if body is None:
        raise Exception("No data sent!")

    key: T.Optional[str] = body.get("key")

    if key is None:
        raise Exception("Key is missing!")

    nonce: T.Optional[str] = body.get("nonce")

    if nonce is None:
        raise Exception("Nonce is missing!")

    ref = str(uuid.uuid4())
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
