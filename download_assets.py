import requests
import os
from AssetBatchConverter import extract_assets

ROOT = os.path.dirname(os.path.realpath(__file__))
RAW = os.path.join(ROOT, "raw")
EXT = os.path.join(ROOT, "extracted")
VERSIONS = os.path.join(ROOT, "versions.txt")


def main():
    path = ROOT
    app_id = "com.nexon.konosuba"

    print("Fetching versions")
    if os.path.exists(VERSIONS):
        with open(VERSIONS, "rt") as f:
            app_version, api_version = f.read().splitlines()
    else:
        print("no local versions found")
        app_version, api_version = update_apk_versions(app_id, path)
    print(app_version, api_version)

    print("Get current resource version")
    try:
        version = get_resource_version(app_version, api_version)
    except Exception as e:
        print("error during resource version request")
        print("updating apk settings")
        update_apk_versions(app_id, path)
        app_version, api_version = update_apk_versions(app_id, path)
        version = get_resource_version(app_version, api_version)

    print(version)

    print("Updating resources/assets")
    update_resources(version)


def get_resource_version(app_version, api_version):
    req = requests.get(
        f"https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/server_config/{app_version}.json",
        headers={
            "User-Agent": "UnityPlayer/2019.4.15f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
            "Accept": "*/*",
            "Accept-Encoding": "deflate, gzip",
            "X-Unity-Version": "2019.4.15f1",
        },
    )
    # {
    # 	"app_version": "1.4.1",
    # 	"asset_version": "1",
    # 	"api_url": "web-prod-konosuba.nexon.com/",
    # 	"asset_url": "nexon.com/",
    # 	"webview_url": "static-stg-konosuba.nexon.com/stg/webview/",
    # 	"banner_url": "static-prod-konosuba.nexon.com/prd/banners/",
    # 	"inquiry_url": "inquiry.nexon.com/",
    # 	"enable_review": "false"
    # }
    res = req.json()

    req = requests.post(
        f"https://api-pub.nexon.com/patch/{api_version}/version-check",
        json={
            "market_game_id": "com.nexon.konosuba",
            "language": "en",
            "advertising_id": "00000000-0000-0000-0000-000000000000",
            "market_code": "playstore",
            "country": "US",
            "sdk_version": "175", # doesn't seem to matter
            "curr_build_version": res["app_version"],
            "curr_build_number": 219, # <- important, has to be extracted from somewhere
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
    # "api_version": "v1.1",
    # "market_game_id": "com.nexon.konosuba",
    # "latest_build_version": "1.4.1",
    # "latest_build_number": "215",
    # "min_build_version": "1.4.1",
    # "min_build_number": "215",
    # "language": "en",
    # "patch": {
    # 	"patch_version": 90,
    # 	"resource_path": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/aa24096586724db2/resource-data.json",
    # 	"bdiff_path": [{
    # 		"89": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/b304171cdc6241d7/bdiff-data.json"
    # 	}, {
    # 		"88": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/4725e6c108e4452f/bdiff-data.json"
    # 	}, {
    # 		"87": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/c483394f9e3d44e6/bdiff-data.json"
    # 	}, {
    # 		"86": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/92f955fb3f9b4c58/bdiff-data.json"
    # 	}, {
    # 		"85": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/21d47e6e3f48462a/bdiff-data.json"
    # 	}, {
    # 		"84": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/d9774a7bf91f433c/bdiff-data.json"
    # 	}, {
    # 		"83": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/76079f9f8a9f43b6/bdiff-data.json"
    # 	}, {
    # 		"82": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/fbc498708ea840b2/bdiff-data.json"
    # 	}, {
    # 		"81": "https://konosuba.dn.nexoncdn.co.kr/com.nexon.konosuba/nxpatch/325a14b912aa48e7/bdiff-data.json"
    # 	}]
    # }
    version = res["patch"]["resource_path"].split("/")[4]
    return version


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


def update_apk_versions(apk_id, path):
    print("downloading latest apk from QooApp")
    apk_data = download_QooApp_apk(apk_id)
    with open(os.path.join(path, "current.apk"), "wb") as f:
        f.write(apk_data)
    print("extracing app_version and api_version")
    app_version, api_version = extract_apk_versions(apk_data)
    with open("versions.txt", "wt") as f:
        f.write("\n".join([app_version, api_version]))

    return app_version, api_version


def extract_apk_versions(apk_data):
    from zipfile import ZipFile
    import io
    import re

    with io.BytesIO(apk_data) as stream:
        with ZipFile(stream) as zip:
            # devs are dumb shit and keep moving the app version around
            for name in zip.namelist():
                if name.startswith("assets/bin/Data/Managed"):
                    with zip.open(name) as f:
                        data = f.read()
                        ver = re.search(b"\d+.\d+.\d+_prd_\d+", data)
                        if ver:
                            app_version = ver[0].decode()
                            break
            with zip.open("classes2.dex") as f:
                raw = f.read()
                for match in re.finditer(b"(.)(v\d+\.\d+)\00", raw):
                    if match[1][0] == len(match[2]):
                        api_version = match[2].decode()
    return app_version, api_version


def download_QooApp_apk(apk):
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode

    query = urlencode(
        {
            "supported_abis": "x86,armeabi-v7a,armeabi",
            "sdk_version": "22",
        }
    )
    res = urlopen(
        Request(
            url=f"https://api.qoo-app.com/v6/apps/{apk}/download?{query}",
            headers={
                "accept-encoding": "gzip",
                "user-agent": "QooApp 8.1.7",
                "device-id": "80e65e35094bedcc",
            },
            method="GET",
        )
    )
    data = urlopen(res.url).read()
    return data


if __name__ == "__main__":
    main()
