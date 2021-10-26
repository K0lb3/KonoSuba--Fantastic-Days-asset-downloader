import json
import hmac
import base64
import hashlib
from typing import Union


def base64url_decode(input: Union[str, bytes]) -> bytes:
    if isinstance(input, str):
        input = input.encode("ascii")

    rem = len(input) % 4

    if rem > 0:
        input += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input)


def base64url_encode(input: bytes) -> bytes:
    return base64.urlsafe_b64encode(input).replace(b"=", b"")


def jwt_encode(payload, key):
    json_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    header = {"alg": "HS256"}
    json_header = json.dumps(header, separators=(",", ":")).encode()

    segments = []
    segments.append(base64url_encode(json_header))
    segments.append(base64url_encode(json_payload))

    # Segments
    signing_input = b".".join(segments)

    signature = hmac.new(key, msg=signing_input, digestmod=hashlib.sha256).digest()
    segments.append(base64url_encode(signature))

    return b".".join(segments).decode("utf8")


def jwt_decode(token: str):
    header, payload, signature = list(map(base64url_decode, token.split(".")))
    # ignore header and signature
    return json.loads(payload)
