import os
import typing as T

from flask import Blueprint, redirect, request
from pyhiccup.core import _convert_tree, html
from werkzeug.datastructures.structures import ImmutableMultiDict

from cardcraft.app.controllers.cards import card
from cardcraft.app.views.base import hiccpage, trident
from cardcraft.app.views.decks import create_deck, listed, shown
from cardcraft.app.views.navigation import menu
from cardcraft.app.services.db import gamedb
from cardcraft.app.services.mem import mem

controller = Blueprint("decks", __name__)


@controller.route("/decks", methods=["GET"])
async def list_decks():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    decks = await gamedb.decks.find({"owner": identity}).to_list()
    listing: list = [
        "p",
        {"class": "blank"},
        [["span", "No decks!"]],
    ]

    if 0 < len(decks):
        listing = listed(decks)

    return await hiccpage([trident(menu(), listing, ["p", "No deck selected"])])


@controller.route("/web/part/game/decks/<deck_id>", methods=["GET"])
async def show_deck(deck_id: str):
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    deck: T.Optional[dict] = await gamedb.decks.find_one(
        {"id": deck_id, "owner": identity}
    )

    if deck is None:
        raise Exception("Deck not found!")

    used: list = await gamedb.cards.find({"id": {"$in": deck["cards"]}}).to_list()
    used_ids: list = list(map(lambda e: e["id"], used))

    available: list = list(
        filter(lambda e: e["id"] not in used_ids, await gamedb.cards.find({}).to_list())
    )

    return _convert_tree(shown(deck, available, used))


@controller.route("/web/part/game/decks/new", methods=["POST"])
async def store_deck():
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    form: ImmutableMultiDict[str, str] = request.form
    if form is None:
        raise Exception("Form not sent!")

    name: T.Optional[str] = form.get("name")

    if name is None:
        raise Exception("Name is missing!")

    cards: list[str] = form.getlist("card")

    await gamedb.decks.insert_one(
        {"id": os.urandom(16).hex(), "name": name, "cards": cards, "owner": identity}
    )

    return redirect("/decks", code=303)


@controller.route("/web/part/game/decks/<deck_id>", methods=["PUT"])
async def update_deck(deck_id: str):
    sess_id: T.Optional[str] = request.cookies.get("ccraft_sess", None)
    assert sess_id is not None

    identity: T.Optional[str] = mem["session"].get(sess_id, {}).get("key", None)
    assert identity is not None

    form: ImmutableMultiDict[str, str] = request.form

    if form is None:
        raise Exception("Form not sent!")

    name: T.Optional[str] = form.get("name")

    if name is None:
        raise Exception("Name is missing!")

    cards: T.Optional[list[str]] = form.getlist("card")

    if cards is None:
        raise Exception("Cards are missing!")

    await gamedb.decks.update_one(
        {"id": deck_id}, {"$set": {"name": name, "cards": cards, "owner": identity}}
    )

    return await show_deck(deck_id)


@controller.route("/web/part/game/decks/new", methods=["GET"])
async def new_deck():
    available: list = await gamedb.cards.find({}).to_list()

    return html(create_deck(cards=available))
