"""Unit and integration tests for Multi-Model AI Integration Platform & Intelligent Model Router.
"""

import pytest
from app.ai.models.model_engine import AIModelEngine
from app.ai.models.mock_provider import MockModelProvider
from app.ai.models.models import (
    ModelCategory,
    ModelStatus,
)


@pytest.mark.anyio
async def test_universal_model_registry():
    engine = AIModelEngine()
    models_list = await engine.available_models()
    assert len(models_list) >= 7
    categories = [m.category.value for m in models_list]
    assert "coding" in categories
    assert "vision" in categories
    assert "speech" in categories
    assert "embedding" in categories


@pytest.mark.anyio
async def test_intelligent_model_router():
    engine = AIModelEngine()
    coding_route = await engine.route_model(ModelCategory.CODING, "Write python function")
    assert coding_route.selected_model_id == "deepseek-coder:6.7b"
    assert coding_route.confidence_score >= 0.90

    vision_route = await engine.route_model(ModelCategory.VISION, "Analyze screenshot button")
    assert vision_route.selected_model_id == "qwen2.5-vl:7b"

    speech_route = await engine.route_model(ModelCategory.SPEECH, "Transcribe speech")
    assert speech_route.selected_model_id == "whisper-large-v3"


@pytest.mark.anyio
async def test_local_model_manager_and_vram():
    engine = AIModelEngine()
    success = await engine.load_model("deepseek-coder:6.7b")
    assert success is True

    active = await engine.active_models()
    assert len(active) == 1
    assert active[0].model_id == "deepseek-coder:6.7b"

    unloaded = await engine.unload_model("deepseek-coder:6.7b")
    assert unloaded is True
    assert len(await engine.active_models()) == 0


@pytest.mark.anyio
async def test_generation_and_chat():
    engine = AIModelEngine()
    gen_res = await engine.generate("Write quicksort function in Python")
    assert "def " in gen_res.text or "quicksort" in gen_res.text or "Ollama" in gen_res.text
    assert gen_res.token_usage.total_tokens > 0

    chat_res = await engine.chat("Hello Nova, explain design patterns")
    assert len(chat_res.text) > 0


@pytest.mark.anyio
async def test_embedding_and_audio():
    engine = AIModelEngine()
    emb_res = await engine.embed(["Hello world", "Vector search"])
    assert len(emb_res.embeddings) == 2
    assert emb_res.dimensions == 768

    stt_res = await engine.transcribe("sample_speech.wav")
    assert len(stt_res.transcript_or_audio_path) > 0

    tts_res = await engine.speak("Welcome to Nova AI Platform")
    assert "wav" in tts_res.transcript_or_audio_path.lower() or "piper" in tts_res.transcript_or_audio_path.lower()


@pytest.mark.anyio
async def test_vision_and_ocr():
    engine = AIModelEngine()
    vis_res = await engine.vision("screenshot.png", "Find save button")
    assert len(vis_res.description) > 0

    ocr_res = await engine.providers["paddleocr"].process_vision(None)
    assert ocr_res.text_found is not None


@pytest.mark.anyio
async def test_prompt_and_context_managers():
    engine = AIModelEngine()
    rendered = engine.prompt_manager.render_prompt("sys_code_engineer", language="Python", goal="ERP system")
    assert "Python" in rendered
    assert "ERP system" in rendered

    comp = engine.context_manager.compress_context("Hello " * 2000, max_tokens=100)
    assert "[Context Truncated" in comp


@pytest.mark.anyio
async def test_performance_and_token_managers():
    engine = AIModelEngine()
    vram = engine.performance_manager.get_vram_usage()
    assert "used_vram_mb" in vram
    assert vram["max_vram_mb"] == 8192

    usage = engine.token_manager.get_total_usage()
    assert usage.total_tokens >= 0


@pytest.mark.anyio
async def test_mock_model_provider():
    mock = MockModelProvider()
    res = await mock.generate(None)
    assert "[Mock Response]" in res.text

    health = await mock.process_vision(None)
    assert health.description == "Mock Vision Analysis"
