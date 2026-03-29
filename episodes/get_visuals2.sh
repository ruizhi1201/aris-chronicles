#!/bin/bash
PEXELS_KEY="PEXELS_KEY_REDACTED"
OUT_DIR="/home/whoami/.openclaw/workspace/aris-chronicles/episodes/visuals/ep04"

declare -a TERMS=("driving+highway+night" "empty+road+car" "city+billboard+night" "person+phone+texting")

for term in "${TERMS[@]}"; do
  echo "Searching: $term"
  result=$(curl -s -H "Authorization: $PEXELS_KEY" \
    "https://api.pexels.com/videos/search?query=${term}&per_page=3&orientation=landscape")
  
  # Get the HD link from first video
  link=$(echo "$result" | python3 -c "
import sys, json
d = json.load(sys.stdin)
videos = d.get('videos', [])
if not videos:
    print('')
    sys.exit()
video = videos[0]
vid_id = video['id']
files = video.get('video_files', [])
best = None
for vf in files:
    if vf.get('file_type') == 'video/mp4':
        if best is None or vf.get('width', 0) > best.get('width', 0):
            best = vf
if best:
    print(f\"{best['link']}|{vid_id}|{best.get('width',0)}x{best.get('height',0)}\")
else:
    print('')
")
  
  if [ -z "$link" ]; then
    echo "  No video found for $term"
    continue
  fi
  
  video_url=$(echo "$link" | cut -d'|' -f1)
  vid_id=$(echo "$link" | cut -d'|' -f2)
  dims=$(echo "$link" | cut -d'|' -f3)
  fname="${term/+/_}_${vid_id}.mp4"
  
  echo "  Downloading $fname ($dims)..."
  curl -sL "$video_url" -o "$OUT_DIR/$fname"
  size=$(stat -c%s "$OUT_DIR/$fname" 2>/dev/null || echo 0)
  echo "  Saved: $fname ($size bytes)"
done

echo ""
echo "Files in visuals dir:"
ls -lh "$OUT_DIR/"
