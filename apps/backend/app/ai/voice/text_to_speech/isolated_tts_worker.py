"""Isolated Multilingual Text-To-Speech (TTS) Worker Script for Nova OS 2.0.

Runs inside the isolated Python 3.11 environment (.venv-stt).
Synthesizes real, authentic multilingual speech:
- Young Female Offline Voice: Windows System SAPI (Microsoft Zira / installed female voice)
  Tuned with youthful cadence (+5% rate) and elevated pitch (+8% to +10%).
- Young Female Neural Voice (Edge-TTS):
  - English (India): en-IN-NeerjaNeural (Female)
  - Tamil (India): ta-IN-PallaviNeural (Female)
  - Hindi (India): hi-IN-SwaraNeural (Female)

Outputs strict JSON metadata to stdout.
"""

import sys
import os
import json
import argparse
import asyncio
import subprocess
import wave


FEMALE_NEURAL_VOICE_MAP = {
    # Indian English Female
    "en-in": "en-IN-NeerjaNeural",
    "en": "en-IN-NeerjaNeural",
    "nova-neural-female": "en-IN-NeerjaNeural",
    "nova-indian-female": "en-IN-NeerjaNeural",
    "nova-indian-pro": "en-IN-NeerjaNeural",
    "neerja": "en-IN-NeerjaNeural",
    # Tamil Female
    "ta-in": "ta-IN-PallaviNeural",
    "ta": "ta-IN-PallaviNeural",
    "nova-tamil-female": "ta-IN-PallaviNeural",
    "nova-tamil-pro": "ta-IN-PallaviNeural",
    "pallavi": "ta-IN-PallaviNeural",
    # Hindi Female
    "hi-in": "hi-IN-SwaraNeural",
    "hi": "hi-IN-SwaraNeural",
    "nova-hindi-female": "hi-IN-SwaraNeural",
    "nova-hindi-pro": "hi-IN-SwaraNeural",
    "swara": "hi-IN-SwaraNeural",
}


def get_installed_sapi_voices() -> list:
    """Dynamically queries installed Windows SAPI voices with metadata."""
    ps_cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$voices = $synth.GetInstalledVoices() | ForEach-Object { "
        "  $v = $_.VoiceInfo; "
        "  $isFem = ($v.Gender.ToString() -eq 'Female' -or $v.Name -match 'Zira|Heera|Hazel|Susan|Linda|Catherine|Eva|Hoda|Naayf|Julie'); "
        "  [PSCustomObject]@{ "
        "    name = $v.Name; "
        "    culture = $v.Culture.Name; "
        "    gender = $v.Gender.ToString(); "
        "    age = $v.Age.ToString(); "
        "    description = $v.Description; "
        "    is_female = $isFem; "
        "    is_default = $_.Enabled; "
        "  } "
        "}; "
        "ConvertTo-Json @($voices)"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            if isinstance(data, dict):
                return [data]
            return data
    except Exception as exc:
        sys.stderr.write(f"Failed to query SAPI voices: {exc}\n")
    return []


def _resolve_neural_female_voice(voice_arg: str, language_arg: str) -> str:
    """Resolves the best authentic young female voice model name for the requested language."""
    if voice_arg and "Neural" in voice_arg:
        return voice_arg

    if voice_arg and voice_arg.lower() in FEMALE_NEURAL_VOICE_MAP:
        return FEMALE_NEURAL_VOICE_MAP[voice_arg.lower()]

    lang = (language_arg or "en-IN").strip().lower()
    if lang.startswith("ta"):
        return "ta-IN-PallaviNeural"
    if lang.startswith("hi"):
        return "hi-IN-SwaraNeural"
    return "en-IN-NeerjaNeural"


def _format_rate(rate_val: float) -> str:
    """Converts rate float (e.g. 1.05, 1.1) to EdgeTTS string (e.g. '+5%', '+10%')."""
    try:
        pct = int(round((rate_val - 1.0) * 100))
        return f"+{pct}%" if pct >= 0 else f"{pct}%"
    except Exception:
        return "+0%"


def _format_pitch(pitch_val: float) -> str:
    """Converts pitch float (e.g. 1.08, 1.0) to EdgeTTS string (e.g. '+4Hz', '+0Hz')."""
    try:
        hz = int(round((pitch_val - 1.0) * 50))
        return f"+{hz}Hz" if hz >= 0 else f"{hz}Hz"
    except Exception:
        return "+0Hz"


async def synthesize_edge_tts(
    text: str,
    output_path: str,
    voice: str,
    rate_str: str,
    pitch_str: str
) -> bool:
    """Synthesizes high-definition neural speech using edge-tts."""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate_str,
            pitch=pitch_str
        )
        await communicate.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 100
    except Exception as exc:
        sys.stderr.write(f"EdgeTTS synthesis failed: {exc}\n")
        return False


def synthesize_local_sapi(
    text: str,
    output_path: str,
    voice_name: str = "",
    rate: float = 1.05,
    pitch: float = 1.08,
    volume: float = 100.0,
) -> tuple[bool, str]:
    """Generates genuine local offline speech via Windows System.Speech SAPI synthesizer.
    Selects female voice by default with youthful tuning (+5% rate, +8% to +10% pitch).
    Returns (success, actual_voice_used).
    """
    try:
        wav_path = output_path
        if not wav_path.lower().endswith(".wav"):
            wav_path = os.path.splitext(output_path)[0] + ".wav"

        # Rate mapping: 1.05 -> Rate = 1
        sapi_int_rate = max(-10, min(10, int(round((rate - 1.0) * 10))))
        # Pitch percentage for SSML: 1.08 -> +8%
        pitch_pct = int(round((pitch - 1.0) * 100))
        pitch_str = f"+{pitch_pct}%" if pitch_pct >= 0 else f"{pitch_pct}%"
        rate_pct = int(round((rate - 1.0) * 100))
        rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
        sapi_vol = max(0, min(100, int(volume)))

        escaped_xml = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "''")
            .replace('"', "&quot;")
        )
        plain_escaped = text.replace("'", "''")

        target_voice_clean = voice_name.strip().replace("'", "''")

        ps_script = (
            "Add-Type -AssemblyName System.Speech; "
            "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$target = '{target_voice_clean}'; "
            "$installed = $synth.GetInstalledVoices() | Select-Object -ExpandProperty VoiceInfo; "
            "if ($target) { "
            "  $matched = $installed | Where-Object { $_.Name -like \"*$target*\" } | Select-Object -First 1; "
            "  if ($matched) { $synth.SelectVoice($matched.Name) } "
            "} else { "
            "  $female = $installed | Where-Object { $_.Gender -eq [System.Speech.Synthesis.VoiceGender]::Female -or $_.Name -match 'Zira|Heera|Hazel|Eva' } | Select-Object -First 1; "
            "  if ($female) { $synth.SelectVoice($female.Name) } "
            "}; "
            f"$synth.Rate = {sapi_int_rate}; "
            f"$synth.Volume = {sapi_vol}; "
            f"$synth.SetOutputToWaveFile('{wav_path}'); "
            "$vCulture = if ($synth.Voice) { $synth.Voice.Culture.Name } else { 'en-US' }; "
            f"$ssml = \"<speak version=''1.0'' xmlns=''http://www.w3.org/2001/10/synthesis'' xml:lang=''$vCulture''>"
            f"<prosody pitch=''{pitch_str}'' rate=''{rate_str}''>{escaped_xml}</prosody></speak>\"; "
            "try { $synth.SpeakSsml($ssml) } catch { $synth.Speak('" + plain_escaped + "') }; "
            "$actualName = if ($synth.Voice) { $synth.Voice.Name } else { 'windows-sapi' }; "
            "$synth.Dispose(); "
            "Write-Output \"VOICE_USED:$actualName\";"
        )

        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=18,
        )

        actual_voice = "Microsoft Zira Desktop"
        for line in res.stdout.splitlines():
            if line.strip().startswith("VOICE_USED:"):
                actual_voice = line.strip().split("VOICE_USED:", 1)[1].strip()
                break

        if res.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 100:
            if wav_path != output_path:
                try:
                    import shutil
                    shutil.copy2(wav_path, output_path)
                except Exception:
                    pass
            return True, actual_voice

        return False, actual_voice
    except Exception as exc:
        sys.stderr.write(f"SAPI synthesis failed: {exc}\n")
        return False, "windows-sapi"


def main():
    parser = argparse.ArgumentParser(description="Isolated TTS Synthesis Worker")
    parser.add_argument("--text", default="", help="Text to speak")
    parser.add_argument("--output", default="", help="Target destination audio file path")
    parser.add_argument("--voice", default="", help="Voice profile or specific voice name")
    parser.add_argument("--language", default="en-IN", help="Target language (en-IN, ta-IN, hi-IN)")
    parser.add_argument("--rate", type=float, default=1.05, help="Speaking rate factor (default 1.05 for youthful speech)")
    parser.add_argument("--pitch", type=float, default=1.08, help="Voice pitch factor (default 1.08 for youthful female voice)")
    parser.add_argument("--volume", type=float, default=100.0, help="Volume level (0-100)")
    parser.add_argument("--offline-only", action="store_true", help="Force local offline synthesis without internet")
    parser.add_argument("--prefer-offline", action="store_true", help="Prioritize 100% local offline synthesis before online services")
    parser.add_argument("--list-sapi-voices", action="store_true", help="Query and output installed Windows SAPI voices as JSON")

    args = parser.parse_args()

    # Dynamic Voice Discovery Mode
    if args.list_sapi_voices:
        voices = get_installed_sapi_voices()
        print(json.dumps(voices))
        sys.exit(0)

    clean_text = args.text.strip()
    if not clean_text:
        print(json.dumps({"success": False, "error": "Text is empty"}))
        sys.exit(1)

    if not args.output:
        print(json.dumps({"success": False, "error": "Output path must be specified"}))
        sys.exit(1)

    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    success = False
    actual_voice_used = ""
    engine_used = "windows-sapi" if (args.prefer_offline or args.offline_only) else "edge-tts"

    # Option A: Local-First Offline Strategy (Windows SAPI Young Female)
    if args.prefer_offline or args.offline_only:
        sapi_voice_hint = args.voice if (args.voice and "Neural" not in args.voice) else ""
        success, actual_voice_used = synthesize_local_sapi(
            clean_text,
            args.output,
            voice_name=sapi_voice_hint,
            rate=args.rate,
            pitch=args.pitch,
            volume=args.volume,
        )
        if success:
            engine_used = "windows-sapi"
        else:
            # Strictly prevent silent escalation to online speech services
            print(json.dumps({
                "success": False,
                "error": "Offline local speech synthesis (Windows SAPI) is unavailable or failed on this machine. "
                         "Silent switching to online TTS is prohibited under Zero-Cost Policy."
            }))
            sys.exit(1)
    else:
        # Option B: Optional Free Online Neural Female (Edge-TTS) with local SAPI fallback
        neural_voice = _resolve_neural_female_voice(args.voice, args.language)
        rate_str = _format_rate(args.rate)
        pitch_str = _format_pitch(args.pitch)

        try:
            success = asyncio.run(
                synthesize_edge_tts(clean_text, args.output, neural_voice, rate_str, pitch_str)
            )
            if success:
                engine_used = "edge-tts"
                actual_voice_used = neural_voice
        except Exception:
            success = False

        if not success:
            # Fall back to local SAPI if network fails
            engine_used = "windows-sapi"
            sapi_voice_hint = args.voice if (args.voice and "Neural" not in args.voice) else ""
            success, actual_voice_used = synthesize_local_sapi(
                clean_text,
                args.output,
                voice_name=sapi_voice_hint,
                rate=args.rate,
                pitch=args.pitch,
                volume=args.volume,
            )

    if not success or not os.path.exists(args.output) or os.path.getsize(args.output) < 100:
        print(json.dumps({
            "success": False,
            "error": "Failed to synthesize audible audio using requested speech engines."
        }))
        sys.exit(1)

    file_size = os.path.getsize(args.output)
    result = {
        "success": True,
        "output_path": os.path.abspath(args.output),
        "engine": engine_used,
        "mode": "offline" if engine_used == "windows-sapi" else "online",
        "voice": actual_voice_used or ("Microsoft Zira Desktop" if engine_used == "windows-sapi" else "en-IN-NeerjaNeural"),
        "language": args.language,
        "bytes": file_size,
        "format": "mp3" if args.output.lower().endswith(".mp3") else "wav",
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
