#!/usr/bin/env python3
"""Ask for a number out loud, record the answer, and transcribe it.

Digits are where speech recognition fails in characteristic ways -- "oh" versus
"zero", "fifteen" versus "fifty", digits run together into one long number --
so this is worth running a few times with different phrasings before designing
anything that asks people for numbers.

    python ask_number.py
    python ask_number.py --prompt "What is your zip code?" --seconds 6
    python ask_number.py --model small.en
"""

import argparse
import subprocess
import time

from faster_whisper import WhisperModel

VOICES_DIR = "../voices"
VOICE = "en_US-lessac-medium"
VOICE_RATE = 22050  # medium-quality Piper voices are 22.05 kHz

RECORD_RATE = 16000  # what whisper wants


def speak(text: str) -> None:
    """Say something through Piper, streaming so playback starts sooner."""
    piper = subprocess.Popen(
        ["python3", "-m", "piper", "--model", VOICE, "--data-dir", VOICES_DIR,
         "--output-raw", "--", text],
        stdout=subprocess.PIPE,
    )
    subprocess.run(
        ["aplay", "-r", str(VOICE_RATE), "-f", "S16_LE", "-t", "raw", "-"],
        stdin=piper.stdout,
        check=True,
    )
    piper.wait()


def record(path: str, seconds: int) -> None:
    subprocess.run(
        ["arecord", "-d", str(seconds), "-f", "S16_LE", "-c", "1",
         "-r", str(RECORD_RATE), path],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prompt", default="How many pets do you have?",
                        help="what the device asks")
    parser.add_argument("--seconds", type=int, default=5,
                        help="how long to record the answer (default: 5)")
    parser.add_argument("--model", default="tiny.en",
                        help="whisper model size (default: tiny.en)")
    parser.add_argument("--output", default="answer.wav",
                        help="where to save the recording (default: answer.wav)")
    args = parser.parse_args()

    # Load the model before speaking, so the wait happens before the question
    # rather than in the silence after the answer.
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    speak(args.prompt)

    print(f"recording {args.seconds}s ...")
    record(args.output, args.seconds)

    t0 = time.perf_counter()
    segments, info = model.transcribe(args.output, beam_size=1)
    text = " ".join(seg.text.strip() for seg in segments)
    elapsed = time.perf_counter() - t0

    print(f"\nheard: {text}\n")
    print(f"saved            {args.output}")
    print(f"audio duration   {info.duration:.2f}s")
    print(f"transcription    {elapsed:.2f}s")
    print(f"real-time factor {elapsed / info.duration:.2f}x")

    speak(f"I heard, {text}")


if __name__ == "__main__":
    main()
