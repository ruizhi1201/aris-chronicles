#!/bin/bash
set -e

EPISODES_DIR="/home/whoami/.openclaw/workspace/aris-chronicles/episodes"
VISUALS_DIR="$EPISODES_DIR/visuals/ep04"
AUDIO="$EPISODES_DIR/ep04-audio.mp3"
OUT="$EPISODES_DIR/ep04-final.mp4"

# Get audio duration
DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$AUDIO")
echo "Audio duration: $DURATION seconds"

# Video files
V1="$VISUALS_DIR/driving_highway+night_15270404.mp4"
V2="$VISUALS_DIR/empty_road+car_11276661.mp4"
V3="$VISUALS_DIR/city_billboard+night_3633569.mp4"
V4="$VISUALS_DIR/person_phone+texting_12692099.mp4"

# Scale and loop each clip to a segment of the total duration
# 4 segments: each ~90 seconds (total 360s)
SEG=90

echo "Preparing video segments..."

# Scale each video to 1920x1080, loop for SEG seconds
for i in 1 2 3 4; do
  eval "VF=\$V$i"
  ffmpeg -y -stream_loop -1 -i "$VF" -t $SEG \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0a0a1a,setsar=1" \
    -c:v libx264 -preset fast -crf 23 -an \
    "$VISUALS_DIR/seg_${i}.mp4" 2>&1 | tail -2
  echo "  Segment $i done"
done

# Concat all segments
cat > "$VISUALS_DIR/segments.txt" << 'EOF'
file 'seg_1.mp4'
file 'seg_2.mp4'
file 'seg_3.mp4'
file 'seg_4.mp4'
EOF

echo "Concatenating segments..."
ffmpeg -y -f concat -safe 0 -i "$VISUALS_DIR/segments.txt" \
  -c copy "$VISUALS_DIR/all_video.mp4" 2>&1 | tail -2

echo "Adding audio and text overlays..."
ffmpeg -y \
  -i "$VISUALS_DIR/all_video.mp4" \
  -i "$AUDIO" \
  -shortest \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='THE ARIS CHRONICLES':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=60:alpha=0.9,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='Episode 4\: The Hector Year':fontsize=32:fontcolor=0xaaaacc:x=(w-text_w)/2:y=h-80:alpha=0.8" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  "$OUT" 2>&1 | tail -5

echo ""
echo "Final video: $OUT"
ls -lh "$OUT"
