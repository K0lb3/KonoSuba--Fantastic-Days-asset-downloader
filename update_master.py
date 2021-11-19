import os
import json
from lib.api import API

game_api = API()


def main():
    print("fetching masterlist")
    masterlist = game_api.masterlist()

    print("fetching masterdata")
    master_version = masterlist["masterversion"]

    masterdata = []
    master_keys = [item["master_key"] for item in masterlist["masterarray"]]
    for i in range(0, len(master_keys), 10):
        keys = master_keys[i : i + 10]
        masterdata.extend(game_api.masterall(keys)["masterarray"])

    print("dumping masterdata")
    ROOT = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(ROOT, "master")
    os.makedirs(folder, exist_ok=True)
    for item in masterdata:
        print(item["master_key"])
        with open(
            os.path.join(folder, f"{item['master_key']}.json"), "wt", encoding="utf8",
        ) as f:
            json.dump(item["master"], f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
