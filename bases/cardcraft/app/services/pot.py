import functools
import json
import os
import time
import typing as T

from enum import Enum
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment, Confirmed, Finalized
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.message import Message
from solders.pubkey import Pubkey
from solders.rpc.responses import GetFeeForMessageResp, GetTransactionResp
from solders.transaction_status import (
    EncodedVersionedTransaction,
    UiAccountsList,
    UiMessage,
    UiParsedMessage,
    UiRawMessage,
    UiTransaction,
    UiTransactionStatusMeta,
)

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
    def _get_pot_fee(self, lamports: int, ttl: T.Optional[int] = None) -> int:
        """calculate fee for a simluated pot payout

        @todo use the match wallet
        """

        bot: T.Optional[Keypair] = self.get_bot_wallet(idx=1)

        if self.sys is None:
            raise AssertionError("Missing!")

        if bot is None:
            raise AssertionError("Bot cannot be nil-valued!")

        tx = Transaction(
            recent_blockhash=self.connection.get_latest_blockhash().value.blockhash
        ).add(
            transfer(
                TransferParams(
                    from_pubkey=self.sys.pubkey(),
                    to_pubkey=bot.pubkey(),
                    lamports=lamports,
                )
            )
        )

        fee: GetFeeForMessageResp = self.connection.get_fee_for_message(
            tx.compile_message(), commitment=Commitment("confirmed")
        )

        # 2x fee for creating the pot
        # + 2x fee for paying out winner and loser
        multiplier: int = 4

        if fee.value is None:
            return 5000 * multiplier

        return fee.value * multiplier

    def get_bot_wallet(self, idx: int = 1) -> T.Optional[Keypair]:
        if self.sys is None:
            return None

        bot_idx: int = idx + int(os.getenv("SALT_AT_20240930", 1))

        return Keypair.from_seed_and_derivation_path(
            self.sys.to_bytes_array(), f"m/44'/501'/{WalletType.bot.value}'/0'/{idx}"
        )

    def get_bot_balance(self, idx: int = 1) -> T.Optional[int]:
        if self.sys is None:
            raise Exception("System account missing!")

        bot1: T.Optional[Keypair] = self.get_bot_wallet(idx)

        if bot1 is None:
            return None

        return self.connection.get_balance(bot1.pubkey()).value

    def get_match_wallet(self, idx: int) -> T.Optional[Keypair]:
        """?

        @todo WARNING: funding user-created one-off addresses, find a better
              or force the user to fund their own actions
        """
        if self.sys is None:
            return None

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

        fundsig: Signature = self.connection.send_transaction(tx, self.sys).value

        return pair

    def get_match_balance(self, idx: int) -> T.Optional[int]:
        addr: T.Optional[Keypair] = self.get_match_wallet(idx)

        if addr is None:
            return None

        return self.connection.get_balance(addr.pubkey()).value

    def pay_match_balance(self, match: dict) -> T.Optional[str]:
        if "winner" not in match:
            raise AssertionError

        if "created" not in match:
            raise AssertionError

        if "finished" not in match or match["finished"] is None:
            raise AssertionError

        if self.sys is None:
            return None

        pot: T.Optional[Keypair] = self.get_match_wallet(match["created"])

        if pot is None:
            return None

        lamports: int = sum(
            (e.get("pot", {}).get("lamports", 0)) for _, e in match["players"].items()
        )
        fee: int = self.get_pot_fee(lamports)

        if fee < lamports:
            raise AssertionError

        lamports -= fee

        winner: T.Union[Pubkey, T.Any] = Pubkey.from_string(
            self.sys.pubkey()
            if match["winner"] in ["bot1", "bot2", "bot3"]
            else match["winner"]
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
    ) -> T.Optional[object]:
        info: GetTransactionResp = self.connection.get_transaction(
            Signature.from_string(sig), commitment=Commitment(commitment)
        )

        if info.value is None:
            return None

        meta: T.Optional[UiTransactionStatusMeta] = info.value.transaction.meta
        tx: EncodedVersionedTransaction = info.value.transaction.transaction

        if tx is None:
            return None

        if isinstance(tx, UiAccountsList):
            return None

        mesg: T.Union[Message, UiParsedMessage, UiRawMessage, T.Any] = tx.message

        if meta is None:
            return None

        return SimpleNamespace(
            **{
                "debit": mesg.account_keys[0],
                "credit": mesg.account_keys[1],
                "amount": meta.post_balances[1] - meta.pre_balances[1],
            }
        )


pot = Pot()  # singleton
