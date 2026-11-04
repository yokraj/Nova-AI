"""Isolated Whisper STT Worker Script.

Runs inside isolated Python 3.11 environment (.venv-stt) with faster-whisper.
Transcribes local audio files cleanly and outputs JSON results to stdout.
"""

import sys
import json
import argparse
import os

try:
    import av
    _orig_av_open = av.open
    def _safe_av_open(*args, **kwargs):
        kwargs.pop("metadata_errors", None)
        return _orig_av_open(*args, **kwargs)
    av.open = _safe_av_open
except Exception:
    pass

try:
    from faster_whisper import WhisperModel
except ImportError:
    print(json.dumps({"error": "faster-whisper is not installed in STT environment.", "success": False}))
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Isolated Whisper STT Worker")
    parser.add_argument("--audio", required=True, help="Path to input audio file")
    parser.add_argument("--model", default="tiny", help="Whisper model name (tiny, base, tiny.en)")
    parser.add_argument("--language", default=None, help="Audio language ('en', 'ta', 'hi', or auto)")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(json.dumps({"error": f"Audio file not found: {args.audio}", "success": False}))
        sys.exit(1)

    try:
        model_name = args.model
        lang = args.language if args.language and args.language != "auto" else None
        if lang in ["ta", "hi"] and model_name.endswith(".en"):
            model_name = "tiny"

        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        segments, info = model.transcribe(args.audio, language=lang, beam_size=5, vad_filter=True)
        transcript = " ".join([seg.text for seg in segments]).strip()

        lang_prob = getattr(info, "language_probability", 0.95)

        result = {
            "transcript": transcript,
            "confidence": float(lang_prob),
            "language": getattr(info, "language", "en"),
            "duration": float(getattr(info, "duration", 0.0)),
            "success": True,
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": f"Whisper transcription failed: {str(e)}", "success": False}))
        sys.exit(1)


if __name__ == "__main__":
    main()
