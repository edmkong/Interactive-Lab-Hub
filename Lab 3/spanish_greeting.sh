#!/usr/bin/env bash
# Greets me by name with Piper, using a Mexican Spanish voice.
#
# Run from anywhere:  ./greet.sh
# The voice lives in Lab 3/voices, the same place piper_demo.sh keeps its own.

set -euo pipefail

VOICES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/voices"
VOICE="es_MX-ald-medium"

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
  -- "¡Buenas noches, Edmond! Bienvenido a frambuesa." \
  | aplay -r "$RATE" -f S16_LE -t raw -
