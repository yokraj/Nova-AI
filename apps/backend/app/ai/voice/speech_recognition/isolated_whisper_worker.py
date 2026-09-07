"""Isolated Whisper STT Worker Script.

Runs inside isolated Python 3.11 environment (.venv-stt) with faster-whisper.
Transcribes local audio files cleanly and outputs JSON results to stdout.
"""

import sys
import json
import argparse
import os

try:
    from faster_whisper import WhisperModel
except ImportError:
    print(json.dumps({"error": "faster-whisper is not installed in STT environment.", "success": False}))
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Isolated Whisper STT Worker")
    parser.add_argument("--audio", required=True, help="Path to input audio file")
    parser.add_argument("--model", default="tiny.en", help="Whisper model name")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(json.dumps({"error": f"Audio file not found: {args.audio}", "success": False}))
        sys.exit(1)

    try:
        model = WhisperModel(args.model, device="cpu", compute_type="int8")
        segments, info = model.transcribe(args.audio)
        transcript = " ".join([seg.text for seg in segments]).strip()

        lang_prob = getattr(info, "language_probability", 0.95)

        result = {
            "transcript": transcript,
            "confidence": float(lang_prob),
            "language": getattr(info, "language", "en"),
            "success": True,
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": f"Whisper transcription failed: {str(e)}", "success": False}))
        sys.exit(1)


if __name__ == "__main__":
    main()
