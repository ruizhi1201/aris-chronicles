#!/usr/bin/env python3
import os
import json
import subprocess
import sys

script_path = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/ep02-script.md"
output_dir = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/audio-chunks"
api_key = "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"

with open(script_path, "r") as f:
    text = f.read().strip()

# Split into paragraphs
paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
print(f"Total paragraphs: {len(paragraphs)}")

# Group into chunks of ~1200 chars
chunks = []
current_chunk = ""
for para in paragraphs:
    if len(current_chunk) + len(para) + 2 > 1200 and current_chunk:
        chunks.append(current_chunk.strip())
        current_chunk = para
    else:
        current_chunk += ("\n\n" if current_chunk else "") + para

if current_chunk.strip():
    chunks.append(current_chunk.strip())

print(f"Total chunks: {len(chunks)}")
for i, c in enumerate(chunks):
    print(f"Chunk {i+1}: {len(c)} chars")

# Generate TTS for each chunk
chunk_files = []
for i, chunk in enumerate(chunks):
    out_file = os.path.join(output_dir, f"chunk{i+1:02d}.mp3")
    chunk_files.append(out_file)
    
    if os.path.exists(out_file):
        print(f"Chunk {i+1} already exists, skipping")
        continue
    
    print(f"Generating chunk {i+1}/{len(chunks)}...")
    
    payload = json.dumps({
        "model": "tts-1-hd",
        "voice": "onyx",
        "input": chunk
    })
    
    cmd = [
        "curl", "-s",
        "https://api.openai.com/v1/audio/speech",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", payload,
        "--output", out_file
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"ERROR on chunk {i+1}: {result.stderr}")
        sys.exit(1)
    
    # Check file size
    size = os.path.getsize(out_file)
    print(f"  -> {out_file} ({size} bytes)")
    if size < 1000:
        # Something went wrong, print contents
        with open(out_file, "rb") as f:
            print(f"  Content: {f.read()[:200]}")
        sys.exit(1)

print("\nAll chunks generated. Concatenating...")

# Create ffmpeg concat list
concat_list = os.path.join(output_dir, "concat.txt")
with open(concat_list, "w") as f:
    for cf in chunk_files:
        f.write(f"file '{cf}'\n")

final_audio = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/ep02-audio.mp3"
cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", final_audio]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"ffmpeg error: {result.stderr}")
    sys.exit(1)

print(f"Audio saved to: {final_audio}")
size = os.path.getsize(final_audio)
print(f"Audio size: {size} bytes")
