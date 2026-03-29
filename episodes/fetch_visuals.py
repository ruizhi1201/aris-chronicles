#!/usr/bin/env python3
import subprocess
import json
import os
import sys

PEXELS_KEY = "2DmeiQ4Xpu1lyE879zjQiZ6ex7H9z40EZ9DabLcpfeYbylE1HSjpZSBw"
OUT_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/visuals/ep02"

queries = [
    ("office meeting", "office_meeting"),
    ("corporate boardroom", "boardroom"),
    ("city commute", "commute"),
    ("person phone typing", "phone_typing"),
]

downloaded = []

for query, label in queries:
    url = f"https://api.pexels.com/videos/search?query={query.replace(' ', '+')}&per_page=3&orientation=landscape"
    print(f"Searching: {query}")
    
    result = subprocess.run([
        "curl", "-s", url,
        "-H", f"Authorization: {PEXELS_KEY}"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Search failed: {result.stderr}")
        continue
    
    try:
        data = json.loads(result.stdout)
    except:
        print(f"  JSON parse failed: {result.stdout[:200]}")
        continue
    
    videos = data.get("videos", [])
    if not videos:
        print(f"  No videos found")
        continue
    
    # Try first video, look for HD mp4
    video = videos[0]
    video_files = video.get("video_files", [])
    
    # Find best HD file (prefer 1920x1080 or highest resolution)
    best = None
    for vf in video_files:
        if vf.get("file_type") == "video/mp4":
            if best is None or (vf.get("width", 0) > best.get("width", 0)):
                best = vf
    
    if not best:
        print(f"  No mp4 found")
        continue
    
    video_url = best["link"]
    out_file = os.path.join(OUT_DIR, f"{label}.mp4")
    
    print(f"  Downloading {best.get('width')}x{best.get('height')} from {video_url[:60]}...")
    
    dl = subprocess.run([
        "curl", "-s", "-L", "-o", out_file, video_url
    ], capture_output=True)
    
    if dl.returncode != 0 or not os.path.exists(out_file) or os.path.getsize(out_file) < 10000:
        print(f"  Download failed or too small")
        if os.path.exists(out_file):
            os.remove(out_file)
        continue
    
    size = os.path.getsize(out_file)
    print(f"  -> {out_file} ({size} bytes)")
    downloaded.append(out_file)

print(f"\nDownloaded {len(downloaded)} video(s): {downloaded}")
