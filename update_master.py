import requests
import os
import json
from base64 import b64decode
from typing import List

# api of the game
game_api = "https://web-prod-konosuba.nexon.com"

# custom api to encrypt/decrypt the api requests and responses
# Please don't request to often from here
# otherwise I will have to take it down.
# Also note, that this api doesn't support the decryption of account specific request.
crypt_api = "http://35.209.217.137"  # might add ssl later on



def main():
    print("fetching masterlist")
    masterlist = get_masterlist()

    print("fetching masterdata")
    master_version = masterlist["masterversion"]
    masterall = get_masterall(
        [item["master_key"] for item in masterlist["masterarray"]]
    )

    print("dumping masterdata")
    ROOT = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(ROOT, "master")
    os.makedirs(folder, exist_ok=True)
    for item in masterall["masterarray"]:
        print(item["master_key"])
        with open(
            os.path.join(folder, f"{item['master_key']}.json"),
            "wt",
            encoding="utf8",
        ) as f:
            json.dump(item["master"], f, ensure_ascii=False, indent=4)


default_body = {"ostype": "A", "masterversion": "-", "client_masterversion": "-"}


def request(path: str, body: dict):
    # 1. encrypt data
    crypt_res = requests.get(f"{crypt_api}/konosuba/encrypt", json=body)
    data = crypt_res.content
    headers = {
        "Host": "web-prod-konosuba.nexon.com",
        "User-Agent": "UnityPlayer/2019.4.15f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "Content-Type": "application/octet-stream",
        "X-Unity-Version": "2019.4.15f1",
        "X-Application-Header": crypt_res.headers["X-Application-Header"],
        "Content-Length": str(len(data)),
    }

    # 2. request to game servers
    game_res = requests.post(f"{game_api}{path}", data=data, headers=headers)

    # 3. decrypt response
    headers = game_res.headers
    del headers["transfer-encoding"]
    crypt_res2 = requests.get(
        f"{crypt_api}/konosuba/decrypt", data=game_res.content, headers=headers
    )

    return crypt_res2.json()


# 1. get masterlist
def get_masterlist():
    body = default_body
    body.update(
        {
            "masterversion": "-",
            "client_masterversion": "-",
        }
    )
    ret = request("/api/masterlist", body)
    # set client_masterversion
    default_body["client_masterversion"] = ret["masterversion"]
    return ret


# 2. get all master files
def get_masterall(master_keys: List[str] = []):
    body = default_body
    body.update(
        {
            "masterversion": default_body["client_masterversion"],
            "master_keys": ",".join(master_keys),
            "client_masterversion": "-",
        }
    )
    ret = request("/api/masterall", body)
    # parse masterdata
    for entry in ret["masterarray"]:
        entry["master"] = json.loads(b64decode(entry["master"]))
    return ret


if __name__ == "__main__":
    main()
