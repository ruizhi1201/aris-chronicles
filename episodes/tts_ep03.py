#!/usr/bin/env python3
import os
import sys
import requests
import subprocess

API_KEY = "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"
WORK_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes"
SCRIPT_FILE = os.path.join(WORK_DIR, "ep03-script.md")
OUTPUT_FILE = os.path.join(WORK_DIR, "ep03-audio.mp3")
CHUNKS_DIR = os.path.join(WORK_DIR, "ep03-chunks")
os.makedirs(CHUNKS_DIR, exist_ok=True)

with open(SCRIPT_FILE, "r") as f:
    text = f.read().strip()

# Split into paragraphs
paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

# Group into chunks of ~1200 chars
chunks = []
current = ""
for p in paragraphs:
    if len(current) + len(p) + 2 > 1200 and current:
        chunks.append(current.strip())
        current = p
    else:
        current = current + "\n\n" + p if current else p
if current:
    chunks.append(current.strip())

print(f"Total chunks: {len(chunks)}")
for i, c in enumerate(chunks):
    print(f"  Chunk {i+1}: {len(c)} chars")

chunk_files = []
for i, chunk in enumerate(chunks):
    out_file = os.path.join(CHUNKS_DIR, f"chunk_{i+1:02d}.mp3")
    chunk_files.append(out_file)
    if os.path.exists(out_file):
        print(f"Chunk {i+1} already exists, skipping.")
        continue
    print(f"Generating chunk {i+1}/{len(chunks)}...")
    resp = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "tts-1-hd", "voice": "onyx", "input": chunk, "response_format": "mp3"}
    )
    if resp.status_code != 200:
        print(f"ERROR on chunk {i+1}: {resp.status_code} {resp.text}")
        sys.exit(1)
    with open(out_file, "wb") as f:
        f.write(resp.content)
    print(f"  Saved {out_file} ({len(resp.content)} bytes)")

# Concatenate with ffmpeg
list_file = os.path.join(CHUNKS_DIR, "chunks.txt")
with open(list_file, "w") as f:
    for cf in chunk_files:
        f.write(f"file '{cf}'\n")

print("Concatenating chunks...")
result = subprocess.run(
    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", OUTPUT_FILE],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("ffmpeg error:", result.stderr)
    sys.exit(1)
print(f"Audio saved to {OUTPUT_FILE}")
