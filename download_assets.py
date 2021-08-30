import requests
import os
from AssetBatchConverter import extract_assets

ROOT = os.path.dirname(os.path.realpath(__file__))
RAW = os.path.join(ROOT, "raw")
EXT = os.path.join(ROOT, "extracted")


def main():
    path = ROOT

    print("Fetch latest resource version")
    check = version_check()
    version = check["patch"]["resource_path"].split("/")[4]
    print(version)

    print("Updating resources/assets")
    update_resources(version)


def version_check(api_version="v1.1", build_version="1.4.1", build_number="208"):
    req = requests.post(
        f"https://api-pub.nexon.com/patch/{api_version}/version-check",
        json={
            "market_game_id": "com.nexon.konosuba",
            "language": "en",
            "advertising_id": "00000000-0000-0000-0000-000000000000",
            "market_code": "playstore",
            "country": "US",
            "sdk_version": "175",  # doesn't seem to matter
            "curr_build_version": build_version,
            "curr_build_number": build_number,
            "curr_patch_version": 0,
        },
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-A908N Build/LMY49I)",
            "Host": "api-pub.nexon.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        },
    )
    res = req.json()

    latest_build_version = res["latest_build_version"]
    latest_build_number = res["latest_build_number"]
    if latest_build_version != build_version or latest_build_number != build_number:
        return version_check(api_version, latest_build_version, latest_build_number)
    return res


def update_resources(version, lang="en"):
    # 1. get resource data
    req = requests.get(
        f"https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/{version}/resource-data.json"
    )
    res = req.json()

    for resource in res["resources"]:
        # {
        # "lang": "ja",
        # "group": "group2",
        # "resource_path": "JA/group2/e392fcd3de13100b67589ef873b1f6d4.bundle",
        # "resource_size": 25206,
        # "resource_hash": "42092be2cf4d14381107205e40ab08b1"
        # },
        if lang and resource["lang"] != lang:
            continue
        update_resource(version, resource)


def update_resource(version, resource):
    url = f"https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/{version}/{resource['resource_path']}"
    raw_path = os.path.join(RAW, *resource["resource_path"].split("/"))
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)

    if not (
        os.path.exists(raw_path)
        and os.path.getsize(raw_path) == resource["resource_size"]
    ):
        print(raw_path)
        data = requests.get(url).content
        with open(raw_path, "wb") as f:
            f.write(data)
        if raw_path.endswith(".bundle"):
            extract_assets(data)
            # extract with UnityPy

if __name__ == "__main__":
    main()