#!/usr/bin/env python3
import subprocess
import os
import json

EPISODES_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes"
VISUALS_DIR = os.path.join(EPISODES_DIR, "visuals/ep02")
AUDIO = os.path.join(EPISODES_DIR, "ep02-audio.mp3")
OUTPUT = os.path.join(EPISODES_DIR, "ep02-final.mp4")
TEMP_DIR = os.path.join(EPISODES_DIR, "video-temp")

os.makedirs(TEMP_DIR, exist_ok=True)

# Get audio duration
result = subprocess.run([
    "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
    "-of", "csv=p=0", AUDIO
], capture_output=True, text=True)
audio_duration = float(result.stdout.strip())
print(f"Audio duration: {audio_duration:.2f}s")

# Get durations of each visual
visual_files = [
    os.path.join(VISUALS_DIR, f)
    for f in ["office_meeting.mp4", "boardroom.mp4", "commute.mp4", "phone_typing.mp4"]
    if os.path.exists(os.path.join(VISUALS_DIR, f))
]

print(f"Visuals: {len(visual_files)}")

# Normalize each visual to 1920x1080, no audio
normalized = []
for i, vf in enumerate(visual_files):
    out = os.path.join(TEMP_DIR, f"norm{i:02d}.mp4")
    normalized.append(out)
    if os.path.exists(out):
        print(f"Norm {i} exists, skipping")
        continue
    print(f"Normalizing {os.path.basename(vf)}...")
    r = subprocess.run([
        "ffmpeg", "-y", "-i", vf,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-r", "24",
        "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        out
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  Normalize error: {r.stderr[-500:]}")
    else:
        print(f"  -> {out}")

# Get durations of normalized clips
clip_durations = []
for nf in normalized:
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", nf
    ], capture_output=True, text=True)
    d = float(r.stdout.strip())
    clip_durations.append(d)
    print(f"  {os.path.basename(nf)}: {d:.2f}s")

total_clip_duration = sum(clip_durations)
print(f"Total clip duration: {total_clip_duration:.2f}s vs audio: {audio_duration:.2f}s")

# Build looped/extended video to cover audio duration
# Strategy: repeat clips in sequence until we exceed audio_duration
loop_list = os.path.join(TEMP_DIR, "loop_concat.txt")
accumulated = 0
entries = []
while accumulated < audio_duration + 5:
    for nf in normalized:
        entries.append(nf)
        idx = normalized.index(nf)
        accumulated += clip_durations[idx]
        if accumulated >= audio_duration + 5:
            break

with open(loop_list, "w") as f:
    for e in entries:
        f.write(f"file '{e}'\n")

print(f"Concat list has {len(entries)} entries, ~{accumulated:.2f}s")

# Concat raw video
raw_video = os.path.join(TEMP_DIR, "raw_video.mp4")
print("Concatenating clips...")
r = subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", loop_list,
    "-c", "copy", raw_video
], capture_output=True, text=True)
if r.returncode != 0:
    print(f"Concat error: {r.stderr[-500:]}")
    exit(1)
print(f"Raw video: {os.path.getsize(raw_video)} bytes")

# Apply dark color grade + title overlays + audio
print("Applying color grade, overlays, and audio...")

drawtext1 = "drawtext=text='THE ARIS CHRONICLES':fontsize=52:fontcolor=white:x=(w-text_w)/2:y=60:alpha=0.9:shadowcolor=black:shadowx=2:shadowy=2"
drawtext2 = "drawtext=text='Episode 2\\: The Product Roadmap for My Soul':fontsize=30:fontcolor=0xaaaacc:x=(w-text_w)/2:y=h-90:alpha=0.85:shadowcolor=black:shadowx=1:shadowy=1"
colorgrade = "curves=r='0/0 0.5/0.4 1/0.8':g='0/0 0.5/0.45 1/0.85':b='0/0.05 0.5/0.5 1/1.0'"

vf = f"{colorgrade},{drawtext1},{drawtext2}"

r = subprocess.run([
    "ffmpeg", "-y",
    "-i", raw_video,
    "-i", AUDIO,
    "-vf", vf,
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    OUTPUT
], capture_output=True, text=True)

if r.returncode != 0:
    print(f"Assembly error: {r.stderr[-1000:]}")
    
    # Try fallback without font (in case font not found)
    print("Trying fallback without custom fonts...")
    r2 = subprocess.run([
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", AUDIO,
        "-vf", colorgrade,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        OUTPUT
    ], capture_output=True, text=True)
    if r2.returncode != 0:
        print(f"Fallback error: {r2.stderr[-500:]}")
        exit(1)
    print("Fallback succeeded (no text overlay)")
else:
    print(f"Success!")

size = os.path.getsize(OUTPUT)
print(f"Final video: {OUTPUT} ({size} bytes, {size/1024/1024:.1f} MB)")
