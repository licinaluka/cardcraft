import functools
import json
import time
import typing as T

from solana.rpc.api import Client
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.signature import Signature
from solders.system_program import TransferParams, transfer
from types import SimpleNamespace


SOLANA_DERIVATION_PATH = (
    "m/44'/501'/0'/0'/0'"  # purpose'/coin-type'/account-idx'/change-idx'/address-idx'
)


def rpriv() -> bytes:
    with open("/tmp/priv", "rb") as f:
        return bytes(json.loads(f.read()))


class Pot:

    # rpc connection
    connection: Client

    # system account
    sys: T.Optional[Keypair] = None

    def __init__(self):
        self.connection = Client("https://api.devnet.solana.com")
        self.sys = Keypair.from_bytes(rpriv())

    def get_pot_fee(self, lamports: int) -> int:
        return self._get_pot_fee(
            (round(lamports, -2) or 1), ttl=(int(time.time() / 3600))
        )

    @functools.lru_cache(maxsize=1)
    def _get_pot_fee(self, lamports: int, ttl: int = None) -> int:
        bot: KeyPair = self.get_bot_wallet()
        assert bot is not None

        """calculate fee for a simluated pot payout"""
        tx = Transaction(
            recent_blockhash=self.connection.get_latest_blockhash().value.blockhash
        ).add(
            transfer(
                TransferParams(
                    from_pubkey=self.sys.pubkey(),
                    to_pubkey=self.get_bot_wallet(idx=1).pubkey(),
                    lamports=lamports,
                )
            )
        )

        fee: object = self.connection.get_fee_for_message(
            tx.compile_message(), commitment="confirmed"
        )

        # 2x fee for creating the pot
        # + 2x fee for paying out winner and loser
        multiplier: int = 4

        return fee.value * multiplier

    def get_bot_wallet(self, idx: int = 1) -> Keypair:
        return Keypair.from_seed_and_derivation_path(
            self.sys.to_bytes_array(), f"m/44'/501'/0'/0'/{idx}"
        )

    def get_bot_balance(self, idx: int = 1) -> int:
        if self.sys is None:
            raise Exception("System account missing!")

        bot1: Keypair = self.get_bot_wallet(idx)
        return self.connection.get_balance(bot1.pubkey()).value

    @functools.cache
    def get_transaction_details(
        self, sig: str, commitment: str = "finalized"
    ) -> object:
        info: object = self.connection.get_transaction(
            Signature.from_string(sig), commitment=commitment
        )
        meta: object = info.value.transaction.meta
        mesg: object = info.value.transaction.transaction.message

        return SimpleNamespace(
            **{
                "debit": mesg.account_keys[0],
                "credit": mesg.account_keys[1],
                "amount": meta.post_balances[1] - meta.pre_balances[1],
            }
        )


pot = Pot()  # singleton
