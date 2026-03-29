#!/usr/bin/env python3
import os
import sys
import textwrap
import requests
import subprocess

API_KEY = "OPENAI_API_KEY_REDACTED"
SCRIPT_PATH = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/ep05-script.md"
OUTPUT_PATH = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/ep05-audio.mp3"
CHUNK_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/chunks"

os.makedirs(CHUNK_DIR, exist_ok=True)

with open(SCRIPT_PATH, "r") as f:
    text = f.read().strip()

# Split into ~1200 char chunks at sentence boundaries
def split_text(text, max_chars=1200):
    sentences = text.replace("\n\n", " <PARA> ").replace("\n", " ").split(". ")
    chunks = []
    current = ""
    for i, sentence in enumerate(sentences):
        part = sentence if sentence.endswith(".") else sentence + "."
        part = part.replace(" <PARA> ", "\n\n")
        if len(current) + len(part) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = part
        else:
            current = current + " " + part if current else part
    if current.strip():
        chunks.append(current.strip())
    return chunks

chunks = split_text(text)
print(f"Split into {len(chunks)} chunks")

chunk_files = []
for i, chunk in enumerate(chunks):
    print(f"Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
    chunk_path = os.path.join(CHUNK_DIR, f"ep05_chunk_{i:03d}.mp3")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "tts-1-hd",
        "voice": "onyx",
        "input": chunk
    }
    
    resp = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"ERROR: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    with open(chunk_path, "wb") as f:
        f.write(resp.content)
    chunk_files.append(chunk_path)
    print(f"  -> saved {chunk_path}")

# Concatenate with ffmpeg
list_file = os.path.join(CHUNK_DIR, "concat_list.txt")
with open(list_file, "w") as f:
    for cf in chunk_files:
        f.write(f"file '{cf}'\n")

cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", OUTPUT_PATH]
print(f"Concatenating {len(chunk_files)} chunks...")
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("ffmpeg error:", result.stderr)
    sys.exit(1)

print(f"Audio saved to {OUTPUT_PATH}")
