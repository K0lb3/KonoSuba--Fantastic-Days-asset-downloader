from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from .jwt_helper import jwt_encode, jwt_decode
import binascii
import json
from requests import Session
from hashlib import md5
from copy import copy


class TextUtil__TypeInfo:
    class static_fields:
        # iv
        _ez_k__BackingField = "h24PZwPkDO4Z"
        _uo_k__BackingField = "ITyq5uo/ZQ=="
        # key
        _ih_k__BackingField = "qG6Dne/0zlf7"
        _ln_k__BackingField = "uJT5Tj0QIQ=="
        # jwt key
        _zr_k__BackingField = "vliDD5J2ohv4"
        _mb_k__BackingField = "1bAGuayJpQ=="

    key = b64decode(
        static_fields._ih_k__BackingField + static_fields._ln_k__BackingField
    )
    iv = b64decode(
        static_fields._ez_k__BackingField + static_fields._uo_k__BackingField
    )
    jwt_key = b64decode(
        static_fields._zr_k__BackingField + static_fields._mb_k__BackingField
    )


class API:
    api: str
    user_key: str
    user_no: str
    default_body: dict
    session: Session

    def __init__(self, api="https://web-prod-konosuba.nexon.com",) -> None:
        self.api = api
        self.user_key = None
        self.user_no = None
        self.session = Session()
        self.session.headers.update(
            {
                "Host": "web-prod-konosuba.nexon.com",
                "User-Agent": "UnityPlayer/2019.4.15f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
                "Accept": "*/*",
                "Accept-Encoding": "deflate, gzip",
                "Content-Type": "application/octet-stream",
                "X-Unity-Version": "2019.4.15f1",
            }
        )
        self.default_body = {
            "ostype": "A",
            "masterversion": "-",
            "client_masterversion": "-",
        }

    def request(self, path: str, body: dict):
        # 1. encrypt data
        data = self.encrypt_request_data(body) if body else None

        # 2. prepare application header
        payload = {"cs": binascii.hexlify(md5(data).digest()).decode()}
        if self.user_key:
            payload["uk"] = self.user_key

        app_header = jwt_encode(payload=payload, key=TextUtil__TypeInfo.jwt_key,)
        self.session.headers["X-Application-Header"] = app_header

        # 3. send
        url = f"{self.api}{path}"
        if self.user_no:
            url += f"?u={self.user_no}"
        self.session.headers["Content-Length"] = str(len(data))
        res = self.session.post(url, data=data)

        # 4. decrypt
        data = self.decrypt_request_data(res)

        return json.loads(data)

    def decrypt_request_data(self, request):
        # iv
        iv = TextUtil__TypeInfo.iv
        app_header = request.headers.get("X-Application-Header", None)
        if app_header:
            # RSA, key ????
            payload = jwt_decode(app_header)

            if payload.get("uk", None):
                self.user_key = payload["uk"]
                print(self.user_key)
                # NetworkUtil_Hex2Bin(payload["uk"], 0x10)
                iv = binascii.unhexlify(payload["uk"])
                iv = b"\x00" * (0x10 - len(iv)) + iv

        # key
        key = TextUtil__TypeInfo.key
        # res = NetworkUtil_Decrypt(request.content, key, iv)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decoded = cipher.decrypt(request.content)
        return unpad(decoded, 0x10, "pkcs7")

    def encrypt_request_data(self, body):
        data = "&".join("=".join(item) for item in body.items()).encode("utf8")

        # iv
        iv = TextUtil__TypeInfo.iv
        if self.user_key:
            iv = binascii.unhexlify(self.user_key)
            iv = b"\x00" * (0x10 - len(iv)) + iv
        # key
        key = TextUtil__TypeInfo.key

        # encode data
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(data, 0x10, "pkcs7"))

    def masterlist(self):
        body = copy(self.default_body)
        body.update(
            {"masterversion": "-", "client_masterversion": "-",}
        )
        ret = self.request("/api/masterlist", body)
        # set client_masterversion
        self.default_body["client_masterversion"] = ret["masterversion"]
        return ret

    def masterall(self, master_keys: list[str] = []):
        body = copy(self.default_body)
        body.update(
            {
                "masterversion": self.default_body["client_masterversion"],
                "master_keys": ",".join(master_keys),
                "client_masterversion": "-",
            }
        )
        ret = self.request("/api/masterall", body)
        # parse masterdata
        for entry in ret["masterarray"]:
            entry["master"] = json.loads(b64decode(entry["master"]))
        return ret
