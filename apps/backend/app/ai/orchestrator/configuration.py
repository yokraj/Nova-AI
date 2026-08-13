"""Configuration settings schema for Universal Multi-Model AI Ecosystem & Intelligent AI Orchestrator.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class OrchestratorConfiguration(BaseModel):
    """System-wide configuration settings for Universal AI Orchestrator."""

    orchestrator_name: str = Field("Universal AI Orchestrator", description="Human-readable orchestrator name")
    version: str = Field("3.4.18", description="Orchestrator version")
    enabled: bool = Field(True, description="Enable orchestrator execution")
    local_first: bool = Field(True, description="Enforce local-first model inference")
    offline_first: bool = Field(True, description="Enable resilient offline fallback mode")
    default_provider: str = Field("ollama", description="Primary default model provider")
    model_directory: str = Field("C:/NovaAI/Models", description="Local model weights directory")
    cache_directory: str = Field("C:/NovaAI/Cache", description="In-memory response and embeddings cache dir")
    
    # Model defaults
    default_reasoning_model: str = Field("qwen3:8b", description="Default reasoning and general model")
    default_coding_model: str = Field("deepseek-coder:6.7b", description="Default coding and software copilot model")
    default_vision_model: str = Field("qwen2.5-vl:7b", description="Default multimodal vision-language model")
    default_speech_model: str = Field("whisper-large-v3", description="Default speech-to-text model")
    default_tts_model: str = Field("piper-v1", description="Default text-to-speech voice synthesis model")
    default_ocr_model: str = Field("paddleocr-v4", description="Default OCR document and screen model")
    default_embedding_model: str = Field("bge-large-en-v1.5", description="Default dense vector embedding model")
    default_translation_model: str = Field("nllb-200", description="Default neural machine translation model")

    # Resource & Hardware Thresholds
    max_concurrent_inferences: int = Field(8, description="Maximum concurrent active inference requests")
    max_vram_allocation_mb: int = Field(12288, description="Maximum VRAM quota in MB")
    max_ram_allocation_mb: int = Field(24576, description="Maximum RAM quota in MB")
    oom_prevention_margin_mb: int = Field(1024, description="Safety VRAM margin for OOM prevention")
    enable_gpu_acceleration: bool = Field(True, description="Enable CUDA/DirectML GPU hardware compute")

    # Streaming & Timeouts
    streaming_chunk_size: int = Field(1, description="Token chunk size for streaming responses")
    default_timeout_seconds: float = Field(30.0, description="Inference request timeout limit")
    health_check_interval_seconds: float = Field(15.0, description="Provider health monitor check interval")

    # Benchmark & Optimization
    enable_auto_benchmarking: bool = Field(True, description="Periodically benchmark installed models")
    enable_prompt_optimization: bool = Field(True, description="Optimize prompts with specialized templates")
    enable_cache: bool = Field(True, description="Enable response caching")
    cache_ttl_seconds: int = Field(3600, description="Cache entry TTL in seconds")
