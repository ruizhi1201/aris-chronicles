#!/bin/bash
set -e

WORK_DIR="/home/whoami/.openclaw/workspace/aris-chronicles/episodes"
VISUALS_DIR="$WORK_DIR/visuals/ep03"
AUDIO="$WORK_DIR/ep03-audio.mp3"
OUTPUT="$WORK_DIR/ep03-final.mp4"
TEMP_DIR="$WORK_DIR/ep03-temp"
mkdir -p "$TEMP_DIR"

AUDIO_DURATION=344.784
# Each visual segment: 344.784 / 4 = ~86.2 seconds each

# Scale and loop each visual to 90 seconds (we'll trim to audio at end)
echo "Processing visual clips..."

for i in 1 2 3 4; do
    case $i in
        1) INPUT="$VISUALS_DIR/v1_laptop.mp4" ;;
        2) INPUT="$VISUALS_DIR/v2_notebook.mp4" ;;
        3) INPUT="$VISUALS_DIR/v3_rain.mp4" ;;
        4) INPUT="$VISUALS_DIR/v4_city.mp4" ;;
    esac
    OUT="$TEMP_DIR/seg${i}.mp4"
    echo "  Processing segment $i from $INPUT..."
    ffmpeg -y -stream_loop -1 -i "$INPUT" \
        -t 90 \
        -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,eq=brightness=-0.1:saturation=0.6" \
        -c:v libx264 -preset fast -crf 23 -an \
        "$OUT" 2>/dev/null
    echo "  Done: $OUT"
done

# Concat segments
echo "Concatenating segments..."
cat > "$TEMP_DIR/concat.txt" << EOF
file '$TEMP_DIR/seg1.mp4'
file '$TEMP_DIR/seg2.mp4'
file '$TEMP_DIR/seg3.mp4'
file '$TEMP_DIR/seg4.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i "$TEMP_DIR/concat.txt" \
    -c:v libx264 -preset fast -crf 23 \
    "$TEMP_DIR/video_raw.mp4" 2>/dev/null

echo "Adding overlays and audio..."
# Add text overlays, mix with audio, trim to audio duration
ffmpeg -y -i "$TEMP_DIR/video_raw.mp4" -i "$AUDIO" \
    -vf "drawtext=text='THE ARIS CHRONICLES':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=60:alpha=0.9:shadowcolor=black:shadowx=2:shadowy=2,
         drawtext=text='Episode 3\: 211 Funerals':fontsize=32:fontcolor=0xaaaacc:x=(w-text_w)/2:y=h-80:alpha=0.85:shadowcolor=black:shadowx=2:shadowy=2" \
    -c:v libx264 -preset fast -crf 23 \
    -c:a aac -b:a 192k \
    -shortest \
    "$OUTPUT" 2>/dev/null

echo "Final video: $OUTPUT"
ls -lh "$OUTPUT"
