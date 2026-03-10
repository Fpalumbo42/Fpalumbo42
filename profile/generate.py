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
CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")


def load_config():
    with open(os.path.join(CONFIG_DIR, "config.json")) as f:
        return json.load(f)


def load_palettes():
    with open(os.path.join(CONFIG_DIR, "palettes.json")) as f:
        return json.load(f)["palettes"]


def pick_palette(palettes):
    name = os.environ.get("PALETTE_NAME")
    if name:
        match = next((p for p in palettes if p["name"] == name), None)
        if match:
            return match
        print(f"Warning: palette '{name}' not found, using random.", file=sys.stderr)
    return random.choice(palettes)


def render_template(src, dst, palette):
    with open(src) as f:
        content = f.read()
    for key, value in palette.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    with open(dst, "w") as f:
        f.write(content)
    print(f"  -> {os.path.relpath(dst, REPO_ROOT)}", file=sys.stderr)


def render_all_templates(config, palette):
    for src_name, dst_name in config["templates"].items():
        render_template(
            os.path.join(TEMPLATES_DIR, src_name),
            os.path.join(SCRIPT_DIR, dst_name),
            palette,
        )


def build_stats_options(config, palette):
    stats = config["stats"]
    return (
        f"username={config['username']}"
        f"&show_icons={str(stats['show_icons']).lower()}"
        f"&include_all_commits={str(stats['include_all_commits']).lower()}"
        f"&count_private={str(stats['count_private']).lower()}"
        f"&title_color={palette['A1']}&text_color={palette['TEXT']}"
        f"&bg_color={palette['BG']}&icon_color={palette['A2']}"
        f"&hide_border=true&border_radius=0"
    )


def build_langs_options(config, palette):
    langs = config["langs"]
    return (
        f"username={config['username']}"
        f"&layout={langs['layout']}&langs_count={langs['langs_count']}"
        f"&hide={','.join(langs['hide'])}"
        f"&title_color={palette['A1']}&text_color={palette['TEXT']}"
        f"&bg_color={palette['BG']}&hide_border=true&border_radius=0"
    )


def build_streak_options(config, palette):
    streak = config["streak"]
    return (
        f"user={config['username']}"
        f"&hide_border=true&background={palette['BG']}"
        f"&ring={palette['A1']}&fire={palette['A1']}"
        f"&currStreakLabel={palette['A1']}&currStreakNum={palette['TEXT']}"
        f"&sideNums={palette['TEXT']}&sideLabels={palette['TEXT']}"
        f"&dates={palette['MUTED']}&border_radius=0"
        f"&date_format={streak['date_format']}"
        f"&mode={streak['mode']}"
    )


def write_github_outputs(config, palette):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return

    outputs = {
        "bg": palette["BG"],
        "a1": palette["A1"],
        "a2": palette["A2"],
        "a3": palette["A3"],
        "text": palette["TEXT"],
        **{f"snk_d{i}": palette[f"SNK_D{i}"] for i in range(5)},
        **{f"snk_l{i}": palette[f"SNK_L{i}"] for i in range(5)},
        "stats_options": build_stats_options(config, palette),
        "langs_options": build_langs_options(config, palette),
        "streak_options": build_streak_options(config, palette),
        "palette_name": palette["name"],
    }

    with open(output_file, "a") as f:
        for key, value in outputs.items():
            f.write(f"{key}={value}\n")


def main():
    config = load_config()
    palette = pick_palette(load_palettes())

    city = config["timezone"].split("/")[-1].replace("_", " ")
    palette["CACHE"] = str(int(time.time()))
    palette["DATE"] = datetime.now(ZoneInfo(config["timezone"])).strftime(
        f"%d %b %Y - %H:%M:%S ({city})"
    )
    print(f"palette: {palette['name']}", file=sys.stderr, flush=True)

    render_all_templates(config, palette)
    write_github_outputs(config, palette)


if __name__ == "__main__":
    main()
