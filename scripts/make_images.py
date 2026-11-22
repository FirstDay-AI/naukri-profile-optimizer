"""Render the README demo image and the GitHub social preview.

Usage (from the repo root, needs Pillow):

    python scripts/make_images.py

The demo image is a real `naukri-optimizer check` run on
examples/data_analyst_before.json, so re-run this after changing the rules.
Writes docs/demo.png, docs/demo.gif (before and after, animated) and
docs/social-preview.png.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SAMPLE = "examples/data_analyst_before.json"
AFTER = "examples/data_analyst_after.json"

# FirstDay AI brand colours
PAPER, INK, LIME, COBALT = "#f5f5f0", "#142724", "#dcf881", "#1959eb"
PINK, SOFT, MUTED = "#f1cadd", "#e9ece5", "#8fa39a"

FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/opentype/inter",
             "/Library/Fonts", "C:/Windows/Fonts"]


def font(names, size):
    for n in names:
        for d in FONT_DIRS:
            p = Path(d) / n
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def mono(size, bold=False):
    return font(["DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"], size)


def sans(size, weight="Regular"):
    return font([f"Inter-{weight}.otf", f"InterDisplay-{weight}.otf",
                 "DejaVuSans-Bold.ttf" if weight == "Bold" else "DejaVuSans.ttf"], size)


def run_check(sample=SAMPLE):
    out = subprocess.run([sys.executable, "-m", "naukri_optimizer", "check", sample],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return out.strip("\n").splitlines()


def demo_lines(raw, max_fixes=6, width=92):
    """Trim the real output to fit an image: keep the first fixes, wrap long lines."""
    lines, in_fixes, shown, skipped = [], False, 0, 0
    for line in raw:
        if line.startswith("Fix these first"):
            in_fixes = True
        elif in_fixes and not line.startswith("  -"):
            if skipped:
                lines.append(("dim", f"  ... {skipped} more fixes"))
            in_fixes = False
        if in_fixes and line.startswith("  -"):
            if shown >= max_fixes:
                skipped += 1
                continue
            shown += 1
            wrapped = textwrap.wrap(line, width, subsequent_indent=" " * 11)
            lines.extend(("fix", w) for w in wrapped)
            continue
        if line.startswith("Tip:") or line.startswith("Want a team"):
            continue
        lines.extend(("text", w) for w in (textwrap.wrap(line, width, initial_indent="",
                     subsequent_indent="  ", drop_whitespace=False) or [""]))
    while lines and not lines[-1][1].strip():
        lines.pop()
    return lines


def draw_terminal(cmd, lines, s=2, rows=None, typed=None, cursor=False):
    """Draw a terminal window showing `$ cmd` and its output lines."""
    f, fb = mono(15 * s), mono(15 * s, bold=True)
    lh, pad, bar_h = 22 * s, 28 * s, 34 * s
    cw = f.getlength("M")
    w = int(pad * 2 + cw * 96)
    h = int(bar_h + pad * 2 + lh * ((rows or len(lines)) + 2))
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, w, bar_h], fill="#0d1c19")
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        x = pad + i * 20 * s
        d.ellipse([x, bar_h / 2 - 6 * s, x + 12 * s, bar_h / 2 + 6 * s], fill=c)
    title = "naukri-optimizer check"
    d.text(((w - sans(13 * s).getlength(title)) / 2, bar_h / 2), title, fill=MUTED,
           font=sans(13 * s), anchor="lm")

    y = bar_h + pad
    shown = cmd if typed is None else cmd[:typed]
    d.text((pad, y), "$ ", fill=LIME, font=fb)
    d.text((pad + cw * 2, y), shown, fill=PAPER, font=fb)
    if cursor:
        cx = pad + cw * (2 + len(shown))
        d.rectangle([cx, y + 2 * s, cx + cw, y + lh - 4 * s], fill=LIME)
    y += lh * 2

    for kind, line in lines:
        x = pad
        if kind == "dim":
            d.text((x, y), line, fill=MUTED, font=f)
        elif line.startswith("Naukri profile score"):
            d.text((x, y), line, fill=LIME, font=fb)
        elif line.rstrip().endswith(":") and not line.startswith(" "):
            d.text((x, y), line, fill=LIME, font=fb)
        elif "[" in line and "]" in line and line.startswith("  ") and "/" in line.split("]")[-1]:
            # section bar: colour the filled part lime
            pre, rest = line.split("[", 1)
            barstr, post = rest.split("]", 1)
            d.text((x, y), pre + "[", fill=PAPER, font=f)
            bx = x + cw * (len(pre) + 1)
            filled = barstr.count("#")
            d.text((bx, y), "#" * filled, fill=LIME, font=f)
            d.text((bx + cw * filled, y), "-" * (len(barstr) - filled), fill="#3c5650", font=f)
            d.text((bx + cw * len(barstr), y), "]" + post, fill=PAPER, font=f)
        elif kind == "fix" and line.startswith("  -"):
            pts, msg = line[:9], line[9:]
            d.text((x, y), pts, fill=PINK, font=fb)
            d.text((x + cw * 9, y), msg, fill=PAPER, font=f)
        else:
            d.text((x, y), line, fill=PAPER, font=f)
        y += lh
    return img


def render_demo(path):
    raw = run_check()
    img = draw_terminal(f"naukri-optimizer check {SAMPLE}", demo_lines(raw))
    img.save(path, optimize=True)
    return raw


def render_gif(path):
    """Before and after: type the command, show the score, then the fixed profile."""
    runs = []
    for sample in (SAMPLE, AFTER):
        lines = demo_lines(run_check(sample), max_fixes=4)
        runs.append((f"naukri-optimizer check {sample}", lines))
    rows = max(len(l) for _, l in runs)
    frames, durations = [], []

    def add(img, ms):
        frames.append(img.convert("P", palette=Image.ADAPTIVE, colors=64))
        durations.append(ms)

    for cmd, lines in runs:
        add(draw_terminal(cmd, [], s=1, rows=rows, typed=0, cursor=True), 500)
        for n in range(4, len(cmd) + 1, 4):
            add(draw_terminal(cmd, [], s=1, rows=rows, typed=n, cursor=True), 45)
        add(draw_terminal(cmd, [], s=1, rows=rows, cursor=True), 300)
        for k in range(2, len(lines) + 1, 2):
            add(draw_terminal(cmd, lines[:k], s=1, rows=rows), 70)
        add(draw_terminal(cmd, lines, s=1, rows=rows), 3800)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=True, disposal=1)


def render_social(path, raw):
    w, h = 1280, 640
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    m = 72

    d.rectangle([0, 0, w, 14], fill=COBALT)
    d.text((m, 88), "github.com/FirstDay-AI", fill="#4d5c55", font=sans(26, "Medium"))
    d.text((m, 128), "naukri-profile-", fill=INK, font=sans(76, "Bold"))
    d.text((m, 212), "optimizer", fill=INK, font=sans(76, "Bold"))
    body = sans(30)
    for i, line in enumerate(["Find out why recruiters skip your",
                              "Naukri profile, and fix it in 2 minutes."]):
        d.text((m, 330 + i * 42), line, fill=INK, font=body)
    tags = ["Free", "Open source", "Runs on your machine"]
    x = m
    for t in tags:
        tw = sans(22, "SemiBold").getlength(t)
        d.rectangle([x, 450, x + tw + 32, 494], fill=LIME)
        d.text((x + 16, 472), t, fill=INK, font=sans(22, "SemiBold"), anchor="lm")
        x += tw + 32 + 12
    d.text((m, 548), "by FirstDay AI  ·  firstdayai.in", fill="#4d5c55", font=sans(22, "Medium"))

    # Right-hand card: the real section scores of the sample profile
    cx, cy, cwid, chei = 790, 110, 418, 420
    d.rectangle([cx, cy, cx + cwid, cy + chei], fill=INK)
    score = next(l for l in raw if l.startswith("Naukri profile score"))
    num = score.split(":")[1].split("/")[0].strip()
    d.text((cx + 32, cy + 34), "SAMPLE PROFILE", fill=LIME, font=sans(18, "SemiBold"))
    d.text((cx + 32, cy + 64), num, fill=PAPER, font=sans(96, "Bold"))
    d.text((cx + 40 + sans(96, "Bold").getlength(num), cy + 124), "/ 100", fill=MUTED, font=sans(30))
    rows = [l for l in raw if l.startswith("  ") and "[" in l and "]" in l][:6]
    y = cy + 196
    for r in rows:
        name = r.split("[")[0].strip()
        sc, mx = r.split("]")[1].strip().split("/")
        d.text((cx + 32, y), name, fill=PAPER, font=sans(18))
        bx, bw = cx + 210, 176
        d.rectangle([bx, y + 4, bx + bw, y + 18], fill="#2a3f3b")
        if int(sc):
            d.rectangle([bx, y + 4, bx + bw * int(sc) / int(mx), y + 18], fill=LIME)
        y += 34
    img.save(path, optimize=True)


def main():
    DOCS.mkdir(exist_ok=True)
    raw = render_demo(DOCS / "demo.png")
    render_gif(DOCS / "demo.gif")
    render_social(DOCS / "social-preview.png", raw)
    print("Wrote docs/demo.png, docs/demo.gif and docs/social-preview.png")


if __name__ == "__main__":
    main()
