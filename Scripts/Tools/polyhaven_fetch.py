"""
Downloads PolyHaven (CC0) textures for the project: diffuse, DirectX normal and roughness maps.

    py Scripts/Tools/polyhaven_fetch.py brown_planks_09 painted_plaster_wall --res 2k

Files go to SourceArt/Textures/PolyHaven/<id>/<id>_<map>_<res>.jpg (or .png when jpg is missing).
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "SourceArt", "Textures", "PolyHaven")
MAPS = {"Diffuse": "diff", "nor_dx": "nor_dx", "Rough": "rough"}
HEADERS = {"User-Agent": "HelloGuest-asset-fetch/1.0"}


def fetch_json(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def download(url, path):
    if os.path.exists(path):
        return False
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=120) as response, open(path, "wb") as out:
        out.write(response.read())
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", nargs="+")
    parser.add_argument("--res", default="2k")
    args = parser.parse_args()

    failed = []
    for asset_id in args.ids:
        try:
            files = fetch_json("https://api.polyhaven.com/files/" + asset_id)
        except urllib.error.HTTPError as error:
            print("%s: not found (%s)" % (asset_id, error.code))
            failed.append(asset_id)
            continue
        folder = os.path.join(OUT, asset_id)
        os.makedirs(folder, exist_ok=True)
        for key, short in MAPS.items():
            variants = files.get(key, {}).get(args.res, {})
            fmt = "jpg" if "jpg" in variants else "png" if "png" in variants else None
            if not fmt:
                print("%s: no %s at %s" % (asset_id, key, args.res))
                continue
            path = os.path.join(folder, "%s_%s_%s.%s" % (asset_id, short, args.res, fmt))
            fresh = download(variants[fmt]["url"], path)
            print("%s: %s %s" % (asset_id, short, "downloaded" if fresh else "already there"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
