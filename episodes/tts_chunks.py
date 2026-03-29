#!/usr/bin/env python3
import re

with open('/home/whoami/.openclaw/workspace/aris-chronicles/episodes/ep04-script.md', 'r') as f:
    text = f.read()

# Split into paragraphs
paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

chunks = []
current = ""

for para in paragraphs:
    if len(current) + len(para) + 2 <= 1200:
        current = (current + "\n\n" + para).strip()
    else:
        if current:
            chunks.append(current)
        current = para

if current:
    chunks.append(current)

print(f"Total chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {len(chunk)} chars")
    with open(f'/home/whoami/.openclaw/workspace/aris-chronicles/episodes/chunks/chunk_{i:02d}.txt', 'w') as f:
        f.write(chunk)
