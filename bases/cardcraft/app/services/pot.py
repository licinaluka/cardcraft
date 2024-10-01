import functools
import json
import os
import time
import typing as T

from enum import Enum
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.system_program import TransferParams, transfer
from types import SimpleNamespace


class WalletType(Enum):
    """BIP-0044 path encoding"""

    bot = 1
    match = 2
    # ...


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
        """calculate fee for a simluated pot payout

        @todo use the match wallet
        """

        bot: KeyPair = self.get_bot_wallet()
        assert bot is not None

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
        bot_idx: int = idx + int(os.getenv("SALT_AT_20240930", 1))

        return Keypair.from_seed_and_derivation_path(
            self.sys.to_bytes_array(), f"m/44'/501'/{WalletType.bot.value}'/0'/{idx}"
        )

    def get_bot_balance(self, idx: int = 1) -> int:
        if self.sys is None:
            raise Exception("System account missing!")

        bot1: Keypair = self.get_bot_wallet(idx)
        return self.connection.get_balance(bot1.pubkey()).value

    def get_match_wallet(self, idx: int) -> Keypair:
        """?

        @todo WARNING: funding user-created one-off addresses, find a better
              or force the user to fund their own actions
        """
        match_idx: int = idx + int(os.getenv("SALT_AT_20240930", 1))
        pair: Keypair = Keypair.from_seed_and_derivation_path(
            self.sys.to_bytes_array(),
            f"m/44'/501'/{WalletType.bot.value}'/0'/{match_idx}",
        )

        if 0 < self.connection.get_balance(pair.pubkey()).value:
            return pair

        rent: int = self.connection.get_minimum_balance_for_rent_exemption(0).value
        tx: Transaction = Transaction(
            recent_blockhash=self.connection.get_latest_blockhash().value.blockhash
        )
        tx.add(
            transfer(
                TransferParams(
                    from_pubkey=self.sys.pubkey(),
                    to_pubkey=pair.pubkey(),
                    lamports=rent,
                )
            )
        )

        fundsig: str = self.connection.send_transaction(tx, self.sys).value

        return pair

    def get_match_balance(self, idx: int) -> int:
        addr: Keypair = self.get_match_wallet(idx)
        return self.connection.get_balance(addr.pubkey()).value

    def pay_match_balance(self, match: dict) -> str:
        assert "winner" in match
        assert "created" in match
        assert "finished" in match and match["finished"] is not None

        pot: Keypair = self.get_match_wallet(match["created"])
        lamports: int = sum((e.get("pot", {}).get("lamports", 0)) for _, e in match["players"].items())
        fee: int = self.get_pot_fee(lamports)

        assert fee < lamports
        lamports -= fee

        winner: str = (
            self.sys.pubkey()
            if match["winner"] in ["bot1", "bot2", "bot3"]
            else Pubkey.from_string(match["winner"])
        )

        tx = Transaction(
            recent_blockhash=self.connection.get_latest_blockhash().value.blockhash
        ).add(
            transfer(
                TransferParams(
                    from_pubkey=pot.pubkey(),
                    to_pubkey=winner,
                    lamports=lamports,
                )
            )
        )

        return str(self.connection.send_transaction(tx, pot).value)

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
