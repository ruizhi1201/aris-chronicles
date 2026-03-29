#!/usr/bin/env python3
"""
Generate YouTube/TikTok thumbnails for Aris Chronicles episodes.
1280x720 (YouTube standard).
Layout: dark bg photo + big quote text + episode label + series branding.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, textwrap

EPISODES_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes"
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

EPISODES = {
    1: {"quote": "He had 211 ideas.\nAll of them dead.", "ep_label": "Ep. 1"},
    2: {"quote": "Another Monday.\nAnother meeting\nabout meetings.", "ep_label": "Ep. 2"},
    3: {"quote": "211 funerals,\nheld in silence.", "ep_label": "Ep. 3"},
    4: {"quote": "Hector believed.\nThat was\nthe mistake.", "ep_label": "Ep. 4"},
    5: {"quote": "James never answered.\nThe beta users\nmoved on.", "ep_label": "Ep. 5"},
}

W, H = 1280, 720

def make_thumbnail(ep_num):
    cfg = EPISODES[ep_num]
    bg_path  = f"{EPISODES_DIR}/ep{ep_num:02d}-bg.jpg"
    out_path = f"{EPISODES_DIR}/ep{ep_num:02d}-thumb.jpg"

    # Load and process background
    bg = Image.open(bg_path).convert("RGB")
    bg = bg.resize((W, H), Image.LANCZOS)

    # Darken + slight blur for readability
    bg = ImageEnhance.Brightness(bg).enhance(0.35)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=3))

    draw = ImageDraw.Draw(bg)

    # ── Gradient-like dark overlay at bottom ──────────────────────────
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for y in range(H // 2, H):
        alpha = int(180 * (y - H // 2) / (H // 2))
        ov_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay).convert("RGB")
    draw = ImageDraw.Draw(bg)

    # ── Series name (top left) ────────────────────────────────────────
    try:
        font_series = ImageFont.truetype(FONT_REGULAR, 28)
    except:
        font_series = ImageFont.load_default()
    draw.text((40, 36), "THE ARIS CHRONICLES", font=font_series, fill=(180, 180, 220, 220))

    # ── Episode label (top right) ──────────────────────────────────────
    try:
        font_ep = ImageFont.truetype(FONT_BOLD, 32)
    except:
        font_ep = ImageFont.load_default()
    ep_text = f"[{cfg['ep_label']}]"
    bbox = draw.textbbox((0, 0), ep_text, font=font_ep)
    ep_w = bbox[2] - bbox[0]
    draw.text((W - ep_w - 40, 32), ep_text, font=font_ep, fill=(120, 160, 255))

    # ── Big quote (center) ─────────────────────────────────────────────
    quote_lines = cfg["quote"].split("\n")
    try:
        font_quote = ImageFont.truetype(FONT_BOLD, 88)
    except:
        font_quote = ImageFont.load_default()

    # Measure total text block height
    line_heights = []
    for line in quote_lines:
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        line_heights.append(bbox[3] - bbox[1])
    line_spacing = 14
    total_h = sum(line_heights) + line_spacing * (len(quote_lines) - 1)

    # Draw shadow then text
    y = (H - total_h) // 2 - 20
    for i, line in enumerate(quote_lines):
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        lw = bbox[2] - bbox[0]
        x = (W - lw) // 2
        # Shadow
        draw.text((x + 3, y + 3), line, font=font_quote, fill=(0, 0, 0, 200))
        # Main text
        draw.text((x, y), line, font=font_quote, fill=(255, 255, 255))
        y += line_heights[i] + line_spacing

    # ── Accent line ───────────────────────────────────────────────────
    draw.rectangle([(W//2 - 60, y + 20), (W//2 + 60, y + 24)], fill=(100, 140, 255))

    # ── Bottom tagline ─────────────────────────────────────────────────
    try:
        font_tag = ImageFont.truetype(FONT_REGULAR, 26)
    except:
        font_tag = ImageFont.load_default()
    tag = "A sci-fi story about ideas that never got built"
    bbox = draw.textbbox((0, 0), tag, font=font_tag)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H - 52), tag, font=font_tag, fill=(160, 160, 200))

    bg.save(out_path, "JPEG", quality=95)
    print(f"✅ Ep {ep_num} thumbnail → {out_path}")
    return out_path

if __name__ == "__main__":
    for ep in range(1, 6):
        make_thumbnail(ep)
    print("\nAll thumbnails done.")
