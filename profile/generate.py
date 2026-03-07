#!/usr/bin/env python3
import json
import os
import random
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
USERNAME = "Fpalumbo42"


with open(os.path.join(SCRIPT_DIR, "palettes.json")) as f:
    palettes = json.load(f)["palettes"]

name = os.environ.get("PALETTE_NAME")
palette = next((p for p in palettes if p["name"] == name), None) if name else None
if not palette:
    if name:
        print(f"Warning: palette '{name}' not found, using random.", file=sys.stderr)
    palette = random.choice(palettes)

palette["CACHE"] = str(int(time.time()))
palette["DATE"] = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d %b %Y - %H:%M:%S (Paris)")
print(f"palette: {palette['name']}", file=sys.stderr, flush=True)

# --- Render templates ---


def render(src: str, dst: str) -> None:
    with open(src) as f:
        content = f.read()
    for key, value in palette.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    with open(dst, "w") as f:
        f.write(content)
    print(f"  -> {os.path.relpath(dst, REPO_ROOT)}", file=sys.stderr)


TEMPLATES = {
    "header.template.svg": "header.svg",
    "skills_snake.template.svg": "skills_snake.svg",
    "footer.template.svg": "footer.svg",
    "README.template.md": os.path.join("..", "README.md"),
}

for src_name, dst_name in TEMPLATES.items():
    render(
        os.path.join(TEMPLATES_DIR, src_name),
        os.path.join(SCRIPT_DIR, dst_name),
    )


output_file = os.environ.get("GITHUB_OUTPUT")
if not output_file:
    sys.exit(0)

p = palette
outputs = {
    "bg": p["BG"],
    "a1": p["A1"],
    "a2": p["A2"],
    "a3": p["A3"],
    "text": p["TEXT"],
    **{f"snk_d{i}": p[f"SNK_D{i}"] for i in range(5)},
    **{f"snk_l{i}": p[f"SNK_L{i}"] for i in range(5)},
    "stats_options": (
        f"username={USERNAME}&show_icons=true&include_all_commits=true&count_private=true"
        f"&title_color={p['A1']}&text_color={p['TEXT']}"
        f"&bg_color={p['BG']}&icon_color={p['A2']}&hide_border=true&border_radius=0"
    ),
    "langs_options": (
        f"username={USERNAME}&layout=compact&langs_count=8"
        f"&title_color={p['A1']}&text_color={p['TEXT']}"
        f"&bg_color={p['BG']}&hide_border=true&border_radius=0"
    ),
    "streak_options": (
        f"user={USERNAME}&hide_border=true&background={p['BG']}&ring={p['A1']}&fire={p['A1']}"
        f"&currStreakLabel={p['A1']}&currStreakNum={p['TEXT']}&sideNums={p['TEXT']}"
        f"&sideLabels={p['TEXT']}&dates={p['MUTED']}&border_radius=0"
    ),
    "palette_name": p["name"],
}

with open(output_file, "a") as f:
    for key, value in outputs.items():
        f.write(f"{key}={value}\n")
