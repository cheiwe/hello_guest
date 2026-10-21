"""Generate concept art from the prompts in Docs/PLAN.md (section 5) with the Gemini API.

Run outside Unreal, from the project root:
    py Scripts/Tools/gen_concepts.py --list            # show prompt ids
    py Scripts/Tools/gen_concepts.py guest neighbor    # generate the prompts whose id contains these words
    py Scripts/Tools/gen_concepts.py --all -n 2        # every prompt, two variants each
    py Scripts/Tools/gen_concepts.py --models          # image-capable models available to the key

The key is read from GEMINI_API_KEY (environment, or the Windows user variables if the
running process was started before the variable was added). It is never printed.
Images go to SourceArt/Concepts/<id>_<n>.png; existing files are kept, new variants get the next number.
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "Docs" / "PLAN.md"
OUT_DIR = ROOT / "SourceArt" / "Concepts"
API = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-2.5-flash-image"

TRANSLIT = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
                    ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p",
                     "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya"]))

# Short English ids for the prompts, matched against the Russian headings in PLAN.md.
IDS = {
    "Улица": "street", "Двор дома соседа": "yard", "Деревянный туалет": "outhouse",
    "Крыша со шпилем": "roof_ufo", "Прихожая": "hallway", "Левая комната": "room_crowbar",
    "Правая комната": "study_puzzle", "Лестница на 2-й": "stairs", "Коридор 2-го": "upstairs_hall",
    "Комната с картинами": "apple_room", "Комната с сейфом": "safe_room",
    "Комната с лампочками": "bulb_room", "Подвал с электрощитком": "basement_fusebox",
    "Чердак": "attic_radio", "Закрытый подвал": "secret_basement", "Дом игрока": "player_bedroom",
    "Игрок": "player", "Сосед": "neighbor", "Гость": "guest", "Паук": "spider",
}


def slug(title):
    for prefix, name in IDS.items():
        if title.startswith(prefix):
            return name
    text = "".join(TRANSLIT.get(c, c) for c in title.lower())
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")[:40]


def load_prompts():
    text = PLAN.read_text(encoding="utf-8")
    blocks = re.findall(r"\*\*([^*\n]+)\*\*[^\n]*\n```\n(.*?)\n```", text, re.S)
    style = next(body for title, body in blocks if title.startswith("Стилевой блок"))
    block3d = next(body for title, body in blocks if title.startswith("Для 3D-генерации"))
    style = " ".join(style.split())
    block3d = " ".join(block3d.split())

    prompts = {}
    for title, body in blocks:
        if "[STYLE]" not in body:
            continue
        body = " ".join(body.split()).replace("[STYLE]", style)
        # "[3D-блок]" or "[3D-блок, view from above and front]"
        body = re.sub(r"\[3D-блок(?:,\s*([^\]]*))?\]",
                      lambda m: block3d + (", " + m.group(1) if m.group(1) else ""), body)
        prompts[slug(title)] = (title, body)
    return prompts


def api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key and sys.platform == "win32":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as reg:
                key = winreg.QueryValueEx(reg, "GEMINI_API_KEY")[0]
        except OSError:
            pass
    if not key:
        sys.exit("GEMINI_API_KEY is not set (Windows: user environment variables).")
    return key


def request(method, path, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}/{path}", data=data, method=method,
                                 headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        detail = err.read().decode(errors="replace")
        try:
            detail = json.loads(detail)["error"]["message"]
        except (ValueError, KeyError):
            pass
        raise RuntimeError(f"HTTP {err.code}: {detail}") from None


def list_models(key):
    models = request("GET", "models?pageSize=1000", key).get("models", [])
    for m in models:
        name = m["name"].removeprefix("models/")
        if "image" in name or "imagen" in name:
            print(f"{name:45} {', '.join(m.get('supportedGenerationMethods', []))}")


def generate(key, model, prompt, aspect):
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}},
    }
    result = request("POST", f"models/{model}:generateContent", key, body)
    for cand in result.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline:
                return base64.b64decode(inline["data"])
    reason = result.get("promptFeedback", {}).get("blockReason") or \
        (result.get("candidates") or [{}])[0].get("finishReason", "no image in response")
    raise RuntimeError(f"no image returned ({reason})")


def next_path(name):
    n = 1
    while (OUT_DIR / f"{name}_{n}.png").exists():
        n += 1
    return OUT_DIR / f"{name}_{n}.png"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("filters", nargs="*", help="generate prompts whose id contains any of these words")
    parser.add_argument("--all", action="store_true", help="generate every prompt")
    parser.add_argument("--list", action="store_true", help="list prompt ids and exit")
    parser.add_argument("--show", action="store_true", help="print the full prompts that would be sent")
    parser.add_argument("--models", action="store_true", help="list image models available to the key")
    parser.add_argument("-n", type=int, default=1, help="variants per prompt")
    parser.add_argument("--model", default=os.environ.get("GEMINI_IMAGE_MODEL", DEFAULT_MODEL))
    parser.add_argument("--aspect", help="aspect ratio, default 16:9 for scenes and 3:4 for characters and props")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Russian titles in a Windows console

    prompts = load_prompts()
    if args.list:
        for name, (title, _) in prompts.items():
            print(f"{name:20} {title}")
        return
    if args.models:
        list_models(api_key())
        return

    # An exact id picks just that prompt ("player" is not "player_bedroom"); otherwise match by substring.
    picked = {f2 for f in args.filters for f2 in ([f] if f in prompts else [k for k in prompts if f in k])}
    chosen = {k: v for k, v in prompts.items() if args.all or k in picked}
    if not chosen:
        parser.error("nothing selected: pass prompt ids (see --list) or --all")
    if args.show:
        for name, (_, prompt) in chosen.items():
            print(f"[{name}]\n{prompt}\n")
        return

    key = api_key()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failed = 0
    for name, (title, prompt) in chosen.items():
        aspect = args.aspect or ("3:4" if "A-pose" in prompt or "isolated" in prompt else "16:9")
        for _ in range(args.n):
            path = next_path(name)
            try:
                path.write_bytes(generate(key, args.model, prompt, aspect))
                print(f"ok    {path.relative_to(ROOT)}")
            except RuntimeError as err:
                failed += 1
                print(f"fail  {name}: {err}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
