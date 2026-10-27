"""Generate the README's typing header as static SVGs (light and dark).

Self-hosted instead of readme-typing-svg so the profile has no runtime
dependency on a third-party service. Run: python scripts/typing_svg.py
"""
from pathlib import Path

from PIL import ImageFont

LINES = [
    "Computer engineer, Atılım University ’25",
    "Moving into data engineering",
    "Python · SQL · Google Cloud",
]
# GitHub's own UI stack, so the header matches the surrounding page.
FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
# Segoe UI metrics drive the per-character steps; textLength pins other fonts to the same width.
METRICS_FONT = "C:/Windows/Fonts/segoeui.ttf"
SIZE = 22
WIDTH, HEIGHT = 560, 40
TYPE_S, HOLD_S, ERASE_S = 1.8, 2.2, 0.6  # per line
THEMES = {  # GitHub fgMuted / accent for each theme, both above 4.5:1 on their ground
    "light": ("#59636e", "#0969da"),
    "dark": ("#9198a1", "#4493f8"),
}


def steps(line, font):
    """Cumulative text width after each character."""
    return [font.getlength(line[:i]) for i in range(len(line) + 1)]


def line_group(index, line, font, text_color, caret_color):
    slot = TYPE_S + HOLD_S + ERASE_S
    total = slot * len(LINES)
    widths = steps(line, font)
    full = widths[-1]
    x0 = (WIDTH - full) / 2
    start = index * slot

    # Discrete keyframes: one per typed char, a hold, one per erased char, then hidden.
    times, values = [], []
    if start > 0:
        times.append(0.0)
        values.append(0.0)
    n = len(line)
    for i, w in enumerate(widths):
        times.append(start + TYPE_S * i / n)
        values.append(w)
    erase_start = start + TYPE_S + HOLD_S
    for i, w in enumerate(reversed(widths[:-1])):
        times.append(erase_start + ERASE_S * (i + 1) / n)
        values.append(w)
    key_times = ";".join(f"{t / total:.4f}" for t in times)
    if times[-1] < total:
        key_times += ";1"
        values.append(0.0)
    clip_vals = ";".join(f"{v:.1f}" for v in values)
    caret_vals = ";".join(f"{x0 + v:.1f}" for v in values)
    # Hide the caret outside this line's slot so only one caret is ever visible.
    show = f"{start / total:.4f};{(start + slot) / total:.4f}"
    vis_times = ("0;" if start > 0 else "") + show + (";1" if start + slot < total else "")
    vis_vals = ("hidden;" if start > 0 else "") + "visible;hidden" + (";hidden" if start + slot < total else "")
    baseline = HEIGHT / 2 + SIZE * 0.35

    return f"""
  <clipPath id="c{index}"><rect x="{x0:.1f}" y="0" height="{HEIGHT}" width="0">
    <animate attributeName="width" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{key_times}" values="{clip_vals}"/>
  </rect></clipPath>
  <text x="{x0:.1f}" y="{baseline:.1f}" textLength="{full:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#c{index})" fill="{text_color}">{line}</text>
  <rect y="{(HEIGHT - SIZE * 1.1) / 2:.1f}" width="2" height="{SIZE * 1.1:.1f}" fill="{caret_color}" visibility="hidden">
    <animate attributeName="x" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{key_times}" values="{caret_vals}"/>
    <animate attributeName="visibility" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{vis_times}" values="{vis_vals}"/>
  </rect>"""


def build(theme):
    text_color, caret_color = THEMES[theme]
    font = ImageFont.truetype(METRICS_FONT, SIZE)
    groups = "".join(line_group(i, line, font, text_color, caret_color) for i, line in enumerate(LINES))
    title = ". ".join(LINES)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{title}">
  <title>{title}</title>
  <style>text {{ font-family: {FONT_STACK}; font-size: {SIZE}px; }}</style>{groups}
</svg>
"""


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    for theme in THEMES:
        (out / f"typing-{theme}.svg").write_text(build(theme), encoding="utf-8")
