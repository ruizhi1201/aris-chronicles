#!/usr/bin/env python3
"""
Aris Chronicles — Episode Video Builder (v2)
Improvements:
1. Title = eye-catching quote + [Ep. N] in brackets
2. Big text overlay = narration printed on screen while reading
3. Static background photo (one per episode, from Pexels)
"""

import os, sys, json, textwrap, subprocess, math, shutil, urllib.request, re

EPISODES_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes"
PEXELS_KEY   = "2DmeiQ4Xpu1lyE879zjQiZ6ex7H9z40EZ9DabLcpfeYbylE1HSjpZSBw"
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Per-episode config ────────────────────────────────────────────────────────
EPISODES = {
    1: {
        "quote": "He had 211 ideas. All of them dead.",
        "pexels_query": "airport terminal night moody",
        "bg_color": "0x0a0a1a",
    },
    2: {
        "quote": "Another Monday. Another meeting about meetings.",
        "pexels_query": "office conference room dark cinematic",
        "bg_color": "0x0d0d1a",
    },
    3: {
        "quote": "211 funerals, held in silence.",
        "pexels_query": "graveyard cemetery dark fog",
        "bg_color": "0x080810",
    },
    4: {
        "quote": "Hector believed. That was the mistake.",
        "pexels_query": "startup office late night coding",
        "bg_color": "0x0a1010",
    },
    5: {
        "quote": "James never answered. The beta users moved on.",
        "pexels_query": "abandoned office dark moody",
        "bg_color": "0x10080a",
    },
}

def run(cmd, **kwargs):
    print(f"  $ {cmd[:80]}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"  STDERR: {result.stderr[-300:]}")
        raise RuntimeError(f"Command failed: {cmd[:60]}")
    return result.stdout.strip()

def get_audio_duration(path):
    out = run(f'ffprobe -v quiet -show_entries format=duration -of csv=p=0 "{path}"')
    return float(out)

def download_bg_photo(ep_num, query, out_path):
    """Download a static background photo from Pexels."""
    if os.path.exists(out_path):
        print(f"  Background photo already exists: {out_path}")
        return
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode())
    photos = data.get("photos", [])
    if not photos:
        raise RuntimeError(f"No Pexels photos found for: {query}")
    # Pick the one with best resolution
    photo = photos[0]
    img_url = photo["src"]["large2x"]
    print(f"  Downloading bg photo: {img_url[:60]}...")
    urllib.request.urlretrieve(img_url, out_path)
    print(f"  Saved: {out_path}")

def parse_script(script_path):
    """Extract narration lines from script markdown."""
    with open(script_path) as f:
        content = f.read()
    # Remove markdown headers and stage directions (lines starting with # or [)
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('#') or line.startswith('[') or line.startswith('---'):
            continue
        lines.append(line)
    return lines

def chunk_text_for_timing(lines, total_duration):
    """
    Split script lines into timed chunks that appear on screen.
    Each chunk shows for ~4-6 seconds.
    Returns list of (start_time, end_time, text_line)
    """
    # Estimate: ~150 words per minute for narration
    # Split into chunks of roughly 3-4 sentences
    all_text = ' '.join(lines)
    words = all_text.split()
    words_per_min = 145
    total_words = len(words)
    
    # Chunk into groups of ~15-20 words (about 6-8 seconds each)
    chunk_size = 15
    chunks = []
    i = 0
    while i < len(words):
        chunk = ' '.join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size
    
    if not chunks:
        return []
    
    # Distribute timing evenly
    time_per_chunk = total_duration / len(chunks)
    timed = []
    for idx, chunk in enumerate(chunks):
        start = idx * time_per_chunk
        end = (idx + 1) * time_per_chunk
        timed.append((start, end, chunk))
    
    return timed

def wrap_text(text, max_chars=40):
    """Wrap text to max_chars per line."""
    return textwrap.fill(text, width=max_chars)

def escape_ffmpeg_text(text):
    """Escape special chars for ffmpeg drawtext."""
    text = text.replace('\\', '\\\\')
    text = text.replace("'", "\u2019")   # replace apostrophe with curly quote
    text = text.replace('"', '\u201c')   # replace straight quotes
    text = text.replace(':', '\\:')
    text = text.replace('%', '\\%')
    text = text.replace('\n', ' ')
    return text

def build_drawtext_filters(timed_chunks, quote, ep_num, font_bold, font_regular):
    """
    Build ffmpeg drawtext filter chain:
    - Big centered narration text (changes over time)
    - Episode title bar at bottom
    - Semi-transparent overlay box behind text
    """
    filters = []
    
    # Dark overlay to make text readable over photo
    filters.append(
        "drawbox=x=0:y=ih*0.15:w=iw:h=ih*0.70:color=black@0.65:t=fill"
    )
    
    # Episode header (small, top)
    filters.append(
        f"drawtext=fontfile='{font_bold}'"
        f":text='THE ARIS CHRONICLES'"
        f":fontsize=36:fontcolor=white@0.7"
        f":x=(w-text_w)/2:y=30"
    )
    
    # Narration text chunks (big, center) — each timed
    for (start, end, chunk) in timed_chunks:
        # Wrap to 2-3 lines
        wrapped = textwrap.fill(chunk, width=35)
        escaped = escape_ffmpeg_text(wrapped)
        # Show text only during its time window
        filters.append(
            f"drawtext=fontfile='{font_bold}'"
            f":text='{escaped}'"
            f":fontsize=58"
            f":fontcolor=white"
            f":x=(w-text_w)/2"
            f":y=(h-text_h)/2-20"
            f":line_spacing=12"
            f":enable='between(t,{start:.2f},{end:.2f})'"
        )
    
    # Bottom bar: quote + episode number
    ep_label = f"[Ep. {ep_num}]"
    quote_escaped = escape_ffmpeg_text(f'"{quote}"  {ep_label}')
    filters.append(
        f"drawbox=x=0:y=ih-100:w=iw:h=100:color=black@0.75:t=fill"
    )
    filters.append(
        f"drawtext=fontfile='{font_regular}'"
        f":text='{quote_escaped}'"
        f":fontsize=28:fontcolor=0xddddff@0.95"
        f":x=(w-text_w)/2:y=h-65"
    )
    
    return ",".join(filters)

def build_video(ep_num):
    import urllib.parse
    
    cfg = EPISODES.get(ep_num)
    if not cfg:
        raise ValueError(f"No config for episode {ep_num}")
    
    audio_path  = f"{EPISODES_DIR}/ep{ep_num:02d}-audio.mp3"
    script_path = f"{EPISODES_DIR}/ep{ep_num:02d}-script.md"
    out_path    = f"{EPISODES_DIR}/ep{ep_num:02d}-final.mp4"
    bg_path     = f"{EPISODES_DIR}/ep{ep_num:02d}-bg.jpg"
    temp_bg     = f"{EPISODES_DIR}/ep{ep_num:02d}-bg-scaled.mp4"
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}")
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    print(f"\n🎬 Building Episode {ep_num}")
    print(f"   Quote: {cfg['quote']}")
    
    # 1. Download background photo
    download_bg_photo(ep_num, cfg['pexels_query'], bg_path)
    
    # 2. Get audio duration
    duration = get_audio_duration(audio_path)
    print(f"   Audio duration: {duration:.1f}s ({duration/60:.1f} min)")
    
    # 3. Parse script into timed text chunks
    lines = parse_script(script_path)
    timed_chunks = chunk_text_for_timing(lines, duration)
    print(f"   Text chunks: {len(timed_chunks)}")
    
    # 4. Build filter chain
    vf = build_drawtext_filters(timed_chunks, cfg['quote'], ep_num, FONT_BOLD, FONT_REGULAR)
    
    # 5. Create looped still image video from background photo
    print("   Creating looped background from photo...")
    run(
        f'ffmpeg -y -loop 1 -i "{bg_path}" -t {duration:.2f} '
        f'-vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1" '
        f'-c:v libx264 -preset fast -crf 23 -an "{temp_bg}"'
    )
    
    # 6. Composite text overlays + audio
    # Write vf filter to file to avoid shell quoting issues
    vf_file = f"{EPISODES_DIR}/ep{ep_num:02d}-vf.txt"
    with open(vf_file, 'w') as f:
        f.write(vf)
    print("   Rendering final video with text overlays...")
    result = subprocess.run(
        [
            'ffmpeg', '-y',
            '-i', temp_bg,
            '-i', audio_path,
            '-shortest',
            '-vf', vf,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
            '-c:a', 'aac', '-b:a', '192k',
            out_path
        ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  STDERR (last 500): {result.stderr[-500:]}")
        raise RuntimeError("ffmpeg render failed")
    
    # 7. Cleanup temp
    if os.path.exists(temp_bg):
        os.remove(temp_bg)
    
    size = os.path.getsize(out_path) / (1024*1024)
    print(f"\n✅ Done: {out_path} ({size:.1f} MB)")
    return out_path, cfg['quote']

def get_youtube_title(ep_num, quote):
    """Format the YouTube/TikTok title."""
    return f'"{quote}" [Ep. {ep_num}] — The Aris Chronicles'

if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    out, quote = build_video(ep)
    title = get_youtube_title(ep, quote)
    print(f"\n📺 Suggested title:")
    print(f'   {title}')
