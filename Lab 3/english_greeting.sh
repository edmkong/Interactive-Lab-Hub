#!/usr/bin/env bash
# The same greeting as greet.sh, in English, so the two can be compared.
#
# Run from anywhere:  ./english_greeting.sh

set -euo pipefail

VOICES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/voices"
VOICE="en_US-lessac-medium"

# Medium-quality Piper voices are 22.05 kHz mono; aplay needs to be told, since
# --output-raw sends headerless samples.
RATE=22050

# Download the voice the first time this runs.
if [ ! -f "$VOICES_DIR/$VOICE.onnx" ]; then
  echo "Downloading $VOICE ..."
  python3 -m piper.download_voices "$VOICE" --data-dir "$VOICES_DIR"
fi

python3 -m piper \
  --model "$VOICE" \
  --data-dir "$VOICES_DIR" \
  --output-raw \
  -- "Good evening, Edmond! Welcome to frambuesa." \
  | aplay -r "$RATE" -f S16_LE -t raw -
