#!/usr/bin/env python3
import os
import sys
import requests

PEXELS_KEY = "2DmeiQ4Xpu1lyE879zjQiZ6ex7H9z40EZ9DabLcpfeYbylE1HSjpZSBw"
VISUALS_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/visuals/ep03"
os.makedirs(VISUALS_DIR, exist_ok=True)

QUERIES = [
    ("person laptop home evening", "v1_laptop.mp4"),
    ("empty notebook desk", "v2_notebook.mp4"),
    ("rain window", "v3_rain.mp4"),
    ("city at night", "v4_city.mp4"),
]

headers = {"Authorization": PEXELS_KEY}

for query, filename in QUERIES:
    out_path = os.path.join(VISUALS_DIR, filename)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"Already have {filename}, skipping.")
        continue
    print(f"Searching Pexels for: {query}")
    resp = requests.get(
        "https://api.pexels.com/videos/search",
        params={"query": query, "per_page": 3, "orientation": "landscape"},
        headers=headers
    )
    if resp.status_code != 200:
        print(f"  ERROR {resp.status_code}: {resp.text}")
        continue
    data = resp.json()
    videos = data.get("videos", [])
    if not videos:
        print(f"  No results for '{query}'")
        continue

    # Try to find HD video file
    video = videos[0]
    video_files = video.get("video_files", [])
    # Prefer HD (1920x1080 or 1280x720)
    hd_file = None
    for vf in video_files:
        if vf.get("quality") == "hd" and vf.get("width", 0) >= 1280:
            hd_file = vf
            break
    if not hd_file:
        # fallback: largest file
        hd_file = max(video_files, key=lambda x: x.get("width", 0) * x.get("height", 0), default=None)
    if not hd_file:
        print(f"  No suitable video file found for '{query}'")
        continue

    url = hd_file.get("link")
    print(f"  Downloading from {url[:80]}...")
    try:
        dl = requests.get(url, stream=True, timeout=60)
        dl.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in dl.iter_content(chunk_size=65536):
                f.write(chunk)
        size = os.path.getsize(out_path)
        print(f"  Saved {filename} ({size} bytes)")
    except Exception as e:
        print(f"  Download failed: {e}")
        if os.path.exists(out_path):
            os.remove(out_path)

print("Done fetching visuals.")
