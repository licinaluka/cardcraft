import os
import requests
import typing as T

from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

key: T.Optional[str] = os.getenv("HELIUS_API", None)
host: str = f"https://devnet.helius-rpc.com/?api-key={key}"

params: dict = {}

resp = requests.get(host + "?" + urlencode(params))

print(resp.text)
