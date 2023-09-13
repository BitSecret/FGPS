import json
import os


def safe_save_json(data, path, filename):
    """Avoiding log file corruption."""
    with open(path + filename + "_bk.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    try:
        os.remove(path + filename + ".json")
    except FileNotFoundError:
        pass

    os.rename(path + filename + "_bk.json", path + filename + ".json")


def debug_print(debug, msg):
    if debug:
        print(msg)
