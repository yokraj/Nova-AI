"""12-Stage Manual Validation Script for M3.4.6 Multi-Model AI Integration Platform & Router.
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/backend")))

from app.ai.models import (
    AIModelEngine,
    ModelPlatformConfiguration,
    ModelCategory,
    ModelStatus,
    MockModelProvider,
)
from app.ai.gateway import AIGateway, ProviderRegistry, ModelRegistry, ProviderFactory, RetryPolicy, TimeoutPolicy


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.6 – Multi-Model AI Integration Platform & Router Validation")
    print("==================================================================\n")

    engine = AIModelEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.default_provider_preference == "ollama"
    print("  [OK] AI Models package loaded successfully.\n")

    # Stage 2: Universal Model Registry
    print("Stage 2: Universal Model Registry (Model Metadata & Capabilities)")
    registered_models = await engine.available_models()
    print(f"  * Total Registered Models: {len(registered_models)}")
    for m in registered_models[:4]:
        print(f"  * Model: '{m.model_id}' ({m.name}) | Provider: {m.provider_type} | Category: {m.category.value} | Quant: {m.quantization}")
    assert len(registered_models) >= 7
    print("  [OK] Universal Model Registry verified.\n")

    # Stage 3: Intelligent Model Router
    print("Stage 3: Intelligent Model Router (Dynamic Task Routing)")
    r_code = await engine.route_model(ModelCategory.CODING, "Write python function")
    r_vision = await engine.route_model(ModelCategory.VISION, "Analyze GUI dialog")
    r_speech = await engine.route_model(ModelCategory.SPEECH, "Transcribe user voice")
    r_emb = await engine.route_model(ModelCategory.EMBEDDING, "Generate vector representation")

    print(f"  * CODING Task -> Model: '{r_code.selected_model_id}' (Provider: {r_code.provider_type}, Confidence: {r_code.confidence_score})")
    print(f"  * VISION Task -> Model: '{r_vision.selected_model_id}' (Provider: {r_vision.provider_type})")
    print(f"  * SPEECH Task -> Model: '{r_speech.selected_model_id}' (Provider: {r_speech.provider_type})")
    print(f"  * EMBEDDING Task -> Model: '{r_emb.selected_model_id}' (Provider: {r_emb.provider_type})")

    assert r_code.selected_model_id == "deepseek-coder:6.7b"
    assert r_vision.selected_model_id == "qwen2.5-vl:7b"
    print("  [OK] Intelligent Model Router routed tasks to optimal models.\n")

    # Stage 4: Local Model Manager & VRAM Lifecycle
    print("Stage 4: Local Model Manager (Loading/Unloading & VRAM State)")
    load_ok = await engine.load_model("deepseek-coder:6.7b")
    active_before = await engine.active_models()
    print(f"  * Loaded Model 'deepseek-coder:6.7b': {load_ok}")
    print(f"  * Active Models Count: {len(active_before)}")
    assert len(active_before) == 1

    unload_ok = await engine.unload_model("deepseek-coder:6.7b")
    active_after = await engine.active_models()
    print(f"  * Unloaded Model 'deepseek-coder:6.7b': {unload_ok}")
    print(f"  * Active Models Count After Unload: {len(active_after)}")
    assert len(active_after) == 0
    print("  [OK] Local Model Manager loaded and unloaded models.\n")

    # Stage 5: Model Providers Integration
    print("Stage 5: Model Provider Registry (Local & Remote Backends)")
    providers_count = len(engine.providers)
    print(f"  * Registered Providers: {list(engine.providers.keys())}")
    assert providers_count >= 10
    print("  [OK] All 10 model providers registered.\n")

    # Stage 6: Voice Pipeline Integration (STT Whisper -> LLM -> TTS Piper)
    print("Stage 6: Voice Model Integration (Whisper -> Reasoning -> Piper)")
    stt_res = await engine.transcribe("sample_input.wav")
    llm_res = await engine.chat(f"Answer user voice prompt: '{stt_res.transcript_or_audio_path}'")
    tts_res = await engine.speak(llm_res.text)

    print(f"  1. Whisper STT Transcript: '{stt_res.transcript_or_audio_path}'")
    print(f"  2. LLM Response: '{llm_res.text[:80]}...'")
    print(f"  3. Piper TTS Output File: '{tts_res.transcript_or_audio_path}'")
    assert len(stt_res.transcript_or_audio_path) > 0
    print("  [OK] Voice pipeline completed STT -> LLM -> TTS stream.\n")

    # Stage 7: Vision & OCR Integration
    print("Stage 7: Vision & OCR Pipeline (PaddleOCR & Qwen VL)")
    vis_res = await engine.vision("desktop_screenshot.png", "Find login button")
    ocr_res = await engine.providers["paddleocr"].process_vision(None)
    print(f"  * Qwen VL Vision Output: '{vis_res.description}'")
    print(f"  * PaddleOCR Text Extracted: '{ocr_res.text_found}'")
    assert len(vis_res.description) > 0
    print("  [OK] Vision & OCR engines integrated successfully.\n")

    # Stage 8: Memory & Vector Embedding Integration
    print("Stage 8: Memory Vector Embedding Integration (BGE Embeddings)")
    emb_res = await engine.embed(["System requirements specification", "User authentication service"])
    print(f"  * Embeddings Count: {len(emb_res.embeddings)}")
    print(f"  * Vector Dimensions: {emb_res.dimensions}")
    assert emb_res.dimensions == 768
    print("  [OK] BGE Vector Embedding provider generated 768-dim vectors.\n")

    # Stage 9: Copilot & Swarm Agent Routing
    print("Stage 9: Copilot & Swarm Agent Routing (Optimal Model Per Role)")
    code_route = await engine.route_model(ModelCategory.CODING, "Write FastAPI backend router")
    research_route = await engine.route_model(ModelCategory.RESEARCH, "Summarize web page contents")
    print(f"  * Software Engineer Agent -> Model: '{code_route.selected_model_id}'")
    print(f"  * Research Agent -> Model: '{research_route.selected_model_id}'")
    assert code_route.selected_model_id == "deepseek-coder:6.7b"
    print("  [OK] Optimal models assigned per agent role.\n")

    # Stage 10: Performance & VRAM Manager
    print("Stage 10: Performance & VRAM Manager (Allocation & GPU Telemetry)")
    vram_info = engine.performance_manager.get_vram_usage()
    print(f"  * Max VRAM: {vram_info['max_vram_mb']} MB")
    print(f"  * Used VRAM: {vram_info['used_vram_mb']} MB")
    print(f"  * Free VRAM: {vram_info['free_vram_mb']} MB")
    assert vram_info["max_vram_mb"] == 8192
    print("  [OK] Performance Manager telemetry verified.\n")

    # Stage 11: Prompt, Context & Token Managers
    print("Stage 11: Prompt, Context & Token Managers")
    rendered_prompt = engine.prompt_manager.render_prompt("sys_code_engineer", language="Python", goal="E-Commerce API")
    compressed_ctx = engine.context_manager.compress_context("Context data... " * 1000, max_tokens=50)
    tokens_usage = engine.token_manager.get_total_usage()

    print(f"  * Rendered Prompt: '{rendered_prompt}'")
    print(f"  * Context Compressed: '{compressed_ctx[:60]}...'")
    print(f"  * Total Tokens Tracked: {tokens_usage.total_tokens}")
    assert "Python" in rendered_prompt
    print("  [OK] Prompt, Context, and Token Managers verified.\n")

    # Stage 12: End-to-End Voice & Multi-Model Execution
    print("Stage 12: End-to-End Execution ('Hey Nova, build an e-commerce website')")
    gen_output = await engine.generate("Build an e-commerce website with FastAPI and React", category=ModelCategory.SOFTWARE_ENGINEERING)
    print(f"  * Model Used: '{gen_output.model_id}'")
    print(f"  * Output Snippet: '{gen_output.text[:100]}...'")
    print(f"  * Tokens Processed: {gen_output.token_usage.total_tokens}")
    assert len(gen_output.text) > 0
    print("  [OK] End-to-end multi-model prompt execution completed.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Multi-Model AI Integration Platform & Router Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
