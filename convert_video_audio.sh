#!/bin/bash

# Script to convert convonet_dm.m4v from MP2 audio to AAC audio for browser compatibility
# This will fix the audio playback issue in browsers

INPUT_FILE="convonet/static/assets/img/convonet_dm.m4v"
OUTPUT_FILE="convonet/static/assets/img/convonet_dm_fixed.m4v"

echo "Converting video audio from MP2 to AAC..."
echo "Input: $INPUT_FILE"
echo "Output: $OUTPUT_FILE"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file not found: $INPUT_FILE"
    exit 1
fi

# Convert video: keep H.264 video, convert MP2 audio to AAC
ffmpeg -i "$INPUT_FILE" \
    -c:v copy \
    -c:a aac \
    -b:a 192k \
    -movflags +faststart \
    "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Conversion successful!"
    echo "New file: $OUTPUT_FILE"
    echo ""
    echo "To use the new file, update the video source in convonet_tech_spec.html:"
    echo "  Change: convonet_dm.m4v"
    echo "  To: convonet_dm_fixed.m4v"
else
    echo "✗ Conversion failed. Please check if ffmpeg is installed."
    exit 1
fi

