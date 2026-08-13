"""Unit and integration tests for Real AI Runtime Integration & Local Model Execution Platform.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
from app.ai.runtime.mock_provider import MockRuntimeProvider
from app.ai.runtime.models import (
    DeviceType,
    ModelType,
    RuntimeStatus,
)


@pytest.mark.anyio
async def test_model_profiles_catalog():
    engine = UniversalAIRuntimeEngine()
    profiles = engine.catalog.list_profiles()
    assert len(profiles) >= 8
    model_ids = [p.model_id for p in profiles]
    assert "qwen3-8b-instruct" in model_ids
    assert "deepseek-coder-v2-lite" in model_ids
    assert "qwen2.5-vl-7b" in model_ids
    assert "faster-whisper-large-v3" in model_ids


@pytest.mark.anyio
async def test_resource_scheduler_and_vram():
    engine = UniversalAIRuntimeEngine()
    telemetry = engine.scheduler.get_telemetry()
    assert telemetry.vram_max_mb == 8192
    assert telemetry.ram_max_mb == 16384

    allocated = engine.scheduler.allocate_vram(1024)
    assert allocated is True


@pytest.mark.anyio
async def test_runtime_manager_and_loading():
    engine = UniversalAIRuntimeEngine()
    success = await engine.load_runtime("qwen3-8b-instruct")
    assert success is True

    active = await engine.active_models()
    assert "qwen3-8b-instruct" in active

    unloaded = await engine.manager.unload_model("qwen3-8b-instruct")
    assert unloaded is True


@pytest.mark.anyio
async def test_llm_chat_reasoning_code():
    engine = UniversalAIRuntimeEngine()
    chat_res = await engine.chat("Hello Nova, explain design patterns")
    assert len(chat_res.text_or_data) > 0

    reason_res = await engine.reason("Derive optimal system architecture")
    assert len(reason_res.text_or_data) > 0

    code_res = await engine.code("Write a binary search algorithm in Python")
    assert len(code_res.text_or_data) > 0


@pytest.mark.anyio
async def test_speech_and_tts_runtimes():
    engine = UniversalAIRuntimeEngine()
    stt_res = await engine.transcribe("input_voice.wav")
    assert len(stt_res.text_or_data) > 0

    tts_res = await engine.speak("Welcome to Nova AI Runtime Engine")
    assert "wav" in tts_res.text_or_data.lower()


@pytest.mark.anyio
async def test_vision_and_ocr_runtimes():
    engine = UniversalAIRuntimeEngine()
    vis_res = await engine.vision("screenshot.png", prompt="Find submit button")
    assert "Qwen2.5-VL" in vis_res.text_or_data or "Screen" in vis_res.text_or_data

    ocr_res = await engine.ocr("document_invoice.pdf")
    assert "text" in ocr_res.text_or_data


@pytest.mark.anyio
async def test_embedding_and_translation_runtimes():
    engine = UniversalAIRuntimeEngine()
    emb_res = await engine.embed(["System requirements specification", "Machine learning runtime"])
    assert emb_res.text_or_data["dimensions"] == 1024
    assert len(emb_res.text_or_data["embeddings"]) == 2

    trans_res = await engine.translate("Hello world", target_lang="es")
    assert "NLLB-200" in trans_res.text_or_data or "es" in trans_res.text_or_data


@pytest.mark.anyio
async def test_runtime_health_and_metrics():
    engine = UniversalAIRuntimeEngine()
    await engine.chat("Test prompt")

    status = await engine.runtime_status()
    assert status.is_healthy is True
    assert status.status == RuntimeStatus.HEALTHY

    metrics = await engine.get_metrics()
    assert metrics.total_inferences >= 1


@pytest.mark.anyio
async def test_mock_runtime_provider():
    mock = MockRuntimeProvider()
    gen_res = await mock.mock_generate(None)
    assert "[Mock Runtime Response]" in gen_res.text_or_data

    stt_res = await mock.mock_transcribe("test.wav")
    assert stt_res.text_or_data == "Mock Speech Transcript"
