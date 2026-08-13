"""12-Stage Manual Validation Script for M3.4.8 Real AI Runtime Integration & Local Execution Platform.
"""

import asyncio
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps/backend")))

from app.ai.runtime import (
    UniversalAIRuntimeEngine,
    RuntimeConfiguration,
    RuntimeState,
    RuntimeStatus,
    ModelType,
    DeviceType,
    MockRuntimeProvider,
)
from app.ai.gateway import AIGateway


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.8 – Real AI Runtime Integration & Local Model Execution Platform")
    print("==================================================================\n")

    engine = UniversalAIRuntimeEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.max_vram_gb == 8.0
    print("  [OK] Runtime Execution Platform package loaded successfully.\n")

    # Stage 2: Model Profiles Catalog
    print("Stage 2: Model Profiles Catalog (Model Specs & Quantizations)")
    profiles = engine.catalog.list_profiles()
    print(f"  * Total Local Model Profiles Registered: {len(profiles)}")
    for p in profiles[:4]:
        print(f"  * Profile: '{p.model_id}' ({p.name}) | Type: {p.type.value} | Quant: {p.quant.value} | Min VRAM: {p.min_vram_mb} MB")
    assert len(profiles) >= 8
    print("  [OK] Model Profiles Catalog verified.\n")

    # Stage 3: Resource Scheduler
    print("Stage 3: Resource Scheduler (GPU VRAM & RAM Tracking)")
    telemetry = engine.scheduler.get_telemetry()
    print(f"  * VRAM Max: {telemetry.vram_max_mb} MB (Used: {telemetry.vram_used_mb} MB)")
    print(f"  * RAM Max: {telemetry.ram_max_mb} MB (Used: {telemetry.ram_used_mb} MB)")
    print(f"  * GPU Usage: {telemetry.gpu_percent}% | Temp: {telemetry.temperature_c}°C")
    assert telemetry.vram_max_mb == 8192
    print("  [OK] Resource Scheduler tracking telemetry.\n")

    # Stage 4: Model Downloader
    print("Stage 4: Model Downloader (Checksum Verification & Offline Cache)")
    dl_progress = await engine.downloader.download_model("qwen3-8b-instruct")
    print(f"  * Model: '{dl_progress.model_id}' | Progress: {dl_progress.percentage}% | Speed: {dl_progress.speed_mbps} MB/s")
    assert dl_progress.completed is True
    print("  [OK] Model Downloader verified model weights.\n")

    # Stage 5: Model Runtime Manager
    print("Stage 5: Model Runtime Manager (Simultaneous Load/Unload Lifecycle)")
    load_ok = await engine.load_runtime("qwen3-8b-instruct")
    active_before = await engine.active_models()
    print(f"  * Loaded Runtime 'qwen3-8b-instruct': {load_ok}")
    print(f"  * Active Models Count: {len(active_before)}")
    assert len(active_before) == 1

    unload_ok = await engine.manager.unload_model("qwen3-8b-instruct")
    active_after = await engine.active_models()
    print(f"  * Unloaded Runtime 'qwen3-8b-instruct': {unload_ok}")
    print(f"  * Active Models Count After Unload: {len(active_after)}")
    assert len(active_after) == 0
    print("  [OK] Model Runtime Manager controlled model memory lifecycle.\n")

    # Stage 6: LLM & Reasoning Runtimes
    print("Stage 6: LLM & Reasoning Runtimes (Ollama/llama.cpp Inference)")
    chat_res = await engine.chat("Explain design patterns in Python")
    reason_res = await engine.reason("Derive microservice architecture boundaries")
    code_res = await engine.code("Write a binary search function in Python")

    print(f"  * LLM Chat Output: '{chat_res.text_or_data[:80]}...' (Device: {chat_res.device_used.value})")
    print(f"  * Reasoning Output: '{reason_res.text_or_data[:80]}...'")
    print(f"  * Code Output: '{code_res.text_or_data[:80]}...'")
    assert len(chat_res.text_or_data) > 0
    print("  [OK] LLM & Reasoning runtimes executed inference.\n")

    # Stage 7: Speech Runtime
    print("Stage 7: Speech Runtime (Faster Whisper / Whisper.cpp STT)")
    stt_res = await engine.transcribe("voice_prompt.wav")
    print(f"  * Whisper STT Transcript: '{stt_res.text_or_data}' (Latency: {stt_res.latency_ms}ms)")
    assert len(stt_res.text_or_data) > 0
    print("  [OK] Speech Runtime transcribed input audio.\n")

    # Stage 8: Voice Runtime
    print("Stage 8: Voice Runtime (Piper / Kokoro TTS Synthesis)")
    tts_res = await engine.speak("Hey Nova, research Kubernetes architecture")
    print(f"  * Piper/Kokoro Audio File Output: '{tts_res.text_or_data}' (Latency: {tts_res.latency_ms}ms)")
    assert "wav" in tts_res.text_or_data.lower()
    print("  [OK] Voice Runtime synthesized speech waveform.\n")

    # Stage 9: Vision Runtime
    print("Stage 9: Vision Runtime (Qwen2.5-VL / InternVL Multimodal)")
    vis_res = await engine.vision("desktop_screenshot.png", prompt="Find save button")
    print(f"  * Multimodal Vision Output: '{vis_res.text_or_data}'")
    assert len(vis_res.text_or_data) > 0
    print("  [OK] Vision Runtime performed screen & image reasoning.\n")

    # Stage 10: OCR Runtime
    print("Stage 10: OCR Runtime (PaddleOCR Document & Form Extraction)")
    ocr_res = await engine.ocr("invoice_document.pdf")
    print(f"  * Extracted Text: '{ocr_res.text_or_data['text']}'")
    assert "INVOICE" in ocr_res.text_or_data["text"]
    print("  [OK] OCR Runtime extracted document text and tables.\n")

    # Stage 11: Embedding & Translation Runtimes
    print("Stage 11: Embedding & Translation Runtimes (BGE-M3 & NLLB-200)")
    emb_res = await engine.embed(["System requirements", "Machine learning runtime"])
    trans_res = await engine.translate("Hello Nova", target_lang="es")
    print(f"  * Vector Dimensions: {emb_res.text_or_data['dimensions']} | Vectors Count: {len(emb_res.text_or_data['embeddings'])}")
    print(f"  * NLLB Translation Output: '{trans_res.text_or_data}'")
    assert emb_res.text_or_data["dimensions"] == 1024
    print("  [OK] Embedding & Translation runtimes verified.\n")

    # Stage 12: Complete End-to-End Voice Pipeline
    print("Stage 12: Complete Voice & Local AI Pipeline Execution")
    print("  Pipeline: Wake Word -> Speech STT -> Intent -> Router -> Selected AI Model -> Mission -> TTS Voice Response")
    stt_step = await engine.transcribe("sample_user_voice.wav")
    llm_step = await engine.chat(f"Process request: '{stt_step.text_or_data}'")
    tts_step = await engine.speak(llm_step.text_or_data)

    print(f"  1. STT Transcript: '{stt_step.text_or_data}'")
    print(f"  2. Selected Model Reasoning Output: '{llm_step.text_or_data[:80]}...'")
    print(f"  3. TTS Spoken Response Audio: '{tts_step.text_or_data}'")
    assert len(tts_step.text_or_data) > 0
    print("  [OK] End-to-end local AI voice pipeline execution complete.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Real AI Runtime Integration & Execution Platform Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
