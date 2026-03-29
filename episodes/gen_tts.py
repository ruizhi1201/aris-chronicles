#!/usr/bin/env python3
import os
import glob

OPENAI_API_KEY = "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"

chunks_dir = '/home/whoami/.openclaw/workspace/aris-chronicles/episodes/chunks'
chunks = sorted(glob.glob(f'{chunks_dir}/chunk_*.txt'))

import urllib.request
import json

for chunk_file in chunks:
    idx = os.path.basename(chunk_file).replace('chunk_', '').replace('.txt', '')
    out_file = f'{chunks_dir}/chunk_{idx}.mp3'
    
    if os.path.exists(out_file):
        print(f"Skipping {idx}, already exists")
        continue
    
    with open(chunk_file, 'r') as f:
        text = f.read()
    
    print(f"Generating TTS for chunk {idx} ({len(text)} chars)...")
    
    payload = json.dumps({
        "model": "tts-1-hd",
        "input": text,
        "voice": "onyx",
        "response_format": "mp3"
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    
    with urllib.request.urlopen(req) as resp:
        audio_data = resp.read()
    
    with open(out_file, 'wb') as f:
        f.write(audio_data)
    
    print(f"  Saved {out_file} ({len(audio_data)} bytes)")

print("All chunks done.")
