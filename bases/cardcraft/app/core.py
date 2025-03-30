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
from os.path import dirname, join
from pyhiccup.core import _convert_tree, html

from cardcraft.app.controllers.authn import controller as authn
from cardcraft.app.controllers.cards import card, controller as cards
from cardcraft.app.controllers.decks import controller as decks
from cardcraft.app.controllers.matches import controller as matches
from cardcraft.app.controllers.configuration.sections import controller as sections
from cardcraft.app.services.db import gamedb
from cardcraft.app.services.loop import locked_loop
from cardcraft.app.services.mem import mem
from cardcraft.app.views.base import faq, hiccpage, landing as landingpage, trident
from cardcraft.app.views.navigation import menu, navigation
from cardcraft.app.views.theme import theme

game = Flask(__name__, static_url_path="/game/resources", static_folder="./resources")
game.config["UPLOAD_FOLDER"] = join(dirname(__file__), "resources/app/img")

game.register_blueprint(authn)
game.register_blueprint(cards)
game.register_blueprint(decks)
game.register_blueprint(matches)

# config
game.register_blueprint(sections)

private = os.getenv("PRIVATE_ENGINE", "0")

if private != "1":
    lock = multiprocessing.Lock()
    p = multiprocessing.Process(target=locked_loop, args=(lock,))
    p.start()

    def reloaded(*a):
        p.terminate()
        p.join()
        sys.exit()

    signal.signal(signal.SIGINT, reloaded)


# @game.errorhandler(Exception)
def exceptions(err):
    resp = Response(
        json.dumps({"detail": str(err)}), status=500, mimetype="application/json"
    )
    return resp


@game.route("/game")
async def landing():
    if request.cookies.get("ccraft_sess") is not None:
        return redirect("/home")

    return _convert_tree(landingpage())


@game.route("/game/home", methods=["GET"])
async def home():
    return await hiccpage(
        trident(
            menu(),
            [
                "span",
                {"hx-get": "/game/web/part/game/matches", "hx-trigger": "load"},
                " ",
            ],
            [
                "div",
                {"style": "padding:2em;"},
                "Select a previous match or start a new one",
            ],
        )
    )


@game.route("/game/help", methods=["GET"])
async def help():
    secondary, tertiary = faq()
    return await hiccpage(trident(menu(), secondary, tertiary))


asgi_app = WsgiToAsgi(game)
