#!/usr/bin/env python3
import glob
import re
import sys


def add_background(svg_dir, bg_color):
    for filepath in glob.glob(f"{svg_dir}/*.svg"):
        with open(filepath) as f:
            content = f.read()

        match = re.search(r'viewBox="([^"]+)"', content)
        if match:
            parts = match.group(1).split()
            rect = f'<rect x="{parts[0]}" y="{parts[1]}" width="{parts[2]}" height="{parts[3]}" fill="#{bg_color}"/>'
        else:
            rect = f'<rect width="100%" height="100%" fill="#{bg_color}"/>'

        content = re.sub(r"(<svg[^>]*>)", r"\1" + rect, content, count=1)

        with open(filepath, "w") as f:
            f.write(content)


if __name__ == "__main__":
    add_background(sys.argv[1], sys.argv[2])
