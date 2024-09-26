import json
import typing as T

from solana.rpc.api import Client
from solders.keypair import Keypair

SOLANA_DERIVATION_PATH = "m/44'/501'/0'/0'/0'" # purpose'/coin-type'/account-idx'/change-idx'/address-idx'

def rpriv() -> bytes:
    with open("/tmp/priv", "rb") as f:
        return bytes(json.loads(f.read()))

class Pot:

    # system account
    sys: T.Optional[Keypair] = None

    def __init__(self):
        self.connection = Client("https://api.devnet.solana.com")
        self.sys = Keypair.from_bytes(rpriv())

    def get_bot_balance(self, idx: int = 1) -> int:
        if self.sys is None:
            raise Exception('System account missing!')

        bot1: Keypair = Keypair.from_seed_and_derivation_path(self.sys.to_bytes_array(), f"m/44'/501'/0'/0'/{idx}'")
        return self.connection.get_balance(bot1.pubkey()).value


pot = Pot()  # singleton