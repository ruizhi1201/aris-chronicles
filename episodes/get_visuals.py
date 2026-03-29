#!/usr/bin/env python3
import urllib.request
import json
import os

PEXELS_KEY = "2DmeiQ4Xpu1lyE879zjQiZ6ex7H9z40EZ9DabLcpfeYbylE1HSjpZSBw"
OUT_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/visuals/ep04"

search_terms = [
    "driving highway night",
    "empty road car",
    "city billboard night",
    "person phone texting"
]

downloaded = []

for term in search_terms:
    safe_term = term.replace(" ", "+")
    url = f"https://api.pexels.com/videos/search?query={safe_term}&per_page=3&orientation=landscape"
    
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY})
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        
        videos = data.get("videos", [])
        if not videos:
            print(f"No results for: {term}")
            continue
        
        video = videos[0]
        vid_id = video["id"]
        
        # Find HD file (prefer 1920 or largest)
        video_files = video.get("video_files", [])
        best = None
        for vf in video_files:
            if vf.get("quality") in ("hd", "uhd") and vf.get("file_type") == "video/mp4":
                if best is None or vf.get("width", 0) > best.get("width", 0):
                    best = vf
        
        if not best:
            # fallback to any mp4
            for vf in video_files:
                if vf.get("file_type") == "video/mp4":
                    if best is None or vf.get("width", 0) > best.get("width", 0):
                        best = vf
        
        if not best:
            print(f"No mp4 found for: {term}")
            continue
        
        link = best["link"]
        out_name = f"{term.replace(' ', '_')}_{vid_id}.mp4"
        out_path = os.path.join(OUT_DIR, out_name)
        
        print(f"Downloading {term} -> {out_name} ({best.get('width')}x{best.get('height')})...")
        urllib.request.urlretrieve(link, out_path)
        print(f"  Saved: {out_path} ({os.path.getsize(out_path)} bytes)")
        downloaded.append(out_path)
        
    except Exception as e:
        print(f"Error for '{term}': {e}")

print(f"\nDownloaded {len(downloaded)} videos:")
for d in downloaded:
    print(f"  {d}")
