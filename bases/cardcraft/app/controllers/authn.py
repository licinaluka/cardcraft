import base58
import json
import time
import typing as T
import uuid

from flask import Blueprint, Response, request
from nacl.signing import VerifyKey
from solders.pubkey import Pubkey
from types import SimpleNamespace

from cardcraft.app.services.db import gamedb
from cardcraft.app.services.mem import mem

controller = Blueprint("authn", __name__, url_prefix="/game")


@controller.route("/api/part/game/authn", methods=["POST"])
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

    if ref is None:
        raise AssertionError

    if ref not in mem["session"]:
        raise AssertionError

    if mem["session"][ref]["key"] is None:
        raise AssertionError

    if cid != mem["session"][ref]["cid"]:
        raise AssertionError(json.dumps(mem["session"][ref]))

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


@controller.route("/api/part/game/authn/logout", methods=["GET"])
async def logout():
    """?

    Todo: cookie params for samesite and strict
    """
    return Response(
        status=303,
        headers={"Set-Cookie": f"ccraft_sess=nil;path=/;max-age=1", "Location": "/"},
    )


@controller.route("/api/part/game/authn/challenge", methods=["POST"])
async def challenge():
    """?

    Todo: cookie params for samesite and strict
    """
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
