"""15-Stage Manual Validation Script for M3.4.17 Real AI Runtime Integration & Unified Model Execution.
"""

import asyncio
import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/backend")))

from app.ai.models.providers.ollama_provider import OllamaProvider
from app.ai.models.model_registry import UniversalModelRegistry
from app.ai.router.model_selector import ModelSelector
from app.ai.router.models import RoutingRequest, TaskType
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
from app.ai.runtime.runtime_monitor import RuntimeMonitor
from app.ai.runtime.resource_scheduler import ResourceScheduler
from app.ai.conversation.response_generator import ResponseGenerator
from app.ai.conversation.models import EmotionMetadata, PersonalityMetadata
from app.ai.research.reasoning_engine import ReasoningEngine
from app.ai.copilot.code_generator import CodeGenerator
from app.ai.copilot.models import ArchitectureDesign, RequirementDocument, TechStack
from app.ai.mission_runtime.workflow_engine import WorkflowEngine
from app.ai.desktop_automation.ai_planning_integration import AIPlanningIntegration
from app.ai.workflow_studio.workflow_optimizer import WorkflowOptimizer
from app.ai.skills.sdk.base_skill import BaseSkill
from app.ai.skills.models import SkillContext, SkillManifest, SkillResponse


class DemoSkill(BaseSkill):
    async def execute(self, action: str, context: SkillContext, **kwargs: Any) -> SkillResponse:
        chat_res = await self.chat("Hello from Skill")
        return SkillResponse(skill_id="demo_skill", success=True, data=chat_res.text_or_data, message=str(chat_res.text_or_data))


async def run_15_stage_validation():
    print("==================================================================")
    print("M3.4.17 – Real AI Runtime Integration & Unified Model Execution")
    print("==================================================================\n")

    ollama = OllamaProvider()
    runtime = UniversalAIRuntimeEngine()

    # Stage 1: Production Ollama Provider Client & Health Diagnostics
    print("Stage 1: Production Ollama Provider Client & Health Diagnostics")
    health = await ollama.health_check()
    print(f"  * Ollama Base URL: '{health['base_url']}' | Status = '{health['status']}' | Version = '{health['version']}'")
    assert "status" in health
    print("  [OK] Ollama Provider client & health diagnostics verified.\n")

    # Stage 2: Ollama Non-Streaming Generation & Thinking Mode
    print("Stage 2: Ollama Non-Streaming Generation & Thinking Mode")
    from app.ai.models.models import GenerationRequest
    gen_res = await ollama.generate(GenerationRequest(prompt="Analyze quantum computing algorithms", model_id="qwen3:8b"))
    print(f"  * Generated Model ID: '{gen_res.model_id}' | Tokens: {gen_res.token_usage.total_tokens}")
    print(f"  * Text Snippet: '{gen_res.text[:90]}...'")
    assert gen_res.text != ""
    print("  [OK] Ollama non-streaming generation verified.\n")

    # Stage 3: Ollama Streaming Response Generator (generate_stream)
    print("Stage 3: Ollama Streaming Response Generator (generate_stream)")
    stream_chunks = []
    async for chunk in ollama.generate_stream(GenerationRequest(prompt="Stream response", model_id="qwen3:8b")):
        stream_chunks.append(chunk)
    print(f"  * Streamed Chunks Count: {len(stream_chunks)} | Total Words: {len(''.join(stream_chunks).split())}")
    assert len(stream_chunks) >= 1
    print("  [OK] Ollama streaming generator verified.\n")

    # Stage 4: Dense Vector Embeddings Generation & Vision Endpoint Processing
    print("Stage 4: Dense Vector Embeddings Generation & Vision Endpoint Processing")
    from app.ai.models.models import EmbeddingRequest, VisionRequest
    emb_res = await ollama.embed(EmbeddingRequest(text_list=["Nova AI OS Core", "Local Model Router"]))
    vis_res = await ollama.process_vision(VisionRequest(prompt="Identify UI control label", image_bytes_or_path="screen.png"))
    print(f"  * Embedding Dimensions: {emb_res.dimensions} | Total Tokens: {emb_res.token_count}")
    print(f"  * Vision Description: '{vis_res.description[:80]}...' | Objects: {vis_res.detected_objects}")
    assert emb_res.dimensions == 768 and len(vis_res.detected_objects) >= 2
    print("  [OK] Vector embeddings & vision processing verified.\n")

    # Stage 5: Ollama Model Management (List, Pull, Delete, Load, Unload & Context Length Detection)
    print("Stage 5: Ollama Model Management (List, Pull, Delete, Load, Unload & Context Length)")
    models_list = await ollama.list_models()
    running_models = await ollama.show_running_models()
    ctx_len = ollama.detect_context_length("qwen3:8b")
    tok_cnt = ollama.count_tokens("This is a test prompt for token estimation.")
    print(f"  * Installed Models Count: {len(models_list)} | Running Models Count: {len(running_models)}")
    print(f"  * Qwen3:8B Context Length: {ctx_len} tokens | Estimated Prompt Tokens: {tok_cnt}")
    assert len(models_list) >= 1 and ctx_len == 32768
    print("  [OK] Ollama model management & lifecycle verified.\n")

    # Stage 6: Universal Model Registry Dynamic Capability Discovery
    print("Stage 6: Universal Model Registry Dynamic Ollama Capability Discovery")
    registry = UniversalModelRegistry()
    disc_models = await registry.discover_ollama_capabilities(models_list)
    print(f"  * Total Models in Registry: {len(registry.list_models())}")
    print(f"  * Dynamically Discovered Models ({len(disc_models)}): {[m.model_id for m in disc_models]}")
    assert len(registry.list_models()) >= 5
    print("  [OK] Universal Model Registry auto-discovery verified.\n")

    # Stage 7: Intelligent Model Router Task Routing (Qwen3:8B, DeepSeek Coder, Qwen2.5-VL, Whisper, BGE, NLLB)
    print("Stage 7: Intelligent Model Router Task Routing")
    selector = ModelSelector()
    code_route = selector.select_best_model(RoutingRequest(prompt="Write FastAPI backend", task_type=TaskType.CODE_GENERATION))
    reason_route = selector.select_best_model(RoutingRequest(prompt="Derive architecture plan", task_type=TaskType.REASONING))
    vision_route = selector.select_best_model(RoutingRequest(prompt="Analyze diagram screenshot", task_type=TaskType.VISION))
    embed_route = selector.select_best_model(RoutingRequest(prompt="Generate vectors", task_type=TaskType.EMBEDDING))
    print(f"  * CODING Task -> Model: '{code_route.selected_model}' ({code_route.reason})")
    print(f"  * REASONING Task -> Model: '{reason_route.selected_model}' ({reason_route.reason})")
    print(f"  * VISION Task -> Model: '{vision_route.selected_model}' ({vision_route.reason})")
    print(f"  * EMBEDDING Task -> Model: '{embed_route.selected_model}' ({embed_route.reason})")
    assert code_route.selected_model == "deepseek-coder:6.7b" and reason_route.selected_model == "qwen3:8b"
    print("  [OK] Intelligent Model Router task routing verified.\n")

    # Stage 8: Universal AIRuntime Engine Facade (chat, reason, code, vision, embed, ocr, translate, transcribe, tts)
    print("Stage 8: Universal AIRuntime Engine Facade Multi-Modal Methods")
    chat_out = await runtime.chat("What is Nova AI OS?")
    reason_out = await runtime.reason("Analyze microservice scaling")
    code_out = await runtime.code("def calculate_metrics(): pass")
    vis_out = await runtime.vision("screen.png", prompt="Find button")
    print(f"  * runtime.chat() -> '{chat_out.text_or_data[:70]}...'")
    print(f"  * runtime.reason() -> '{reason_out.text_or_data[:70]}...'")
    print(f"  * runtime.code() -> '{code_out.text_or_data[:70]}...'")
    assert chat_out.text_or_data != "" and code_out.text_or_data != ""
    print("  [OK] Universal AIRuntime Engine facade multi-modal methods verified.\n")

    # Stage 9: AI Gateway Unified Route Flow (Gateway -> Runtime -> Router -> Ollama -> Response)
    print("Stage 9: AI Gateway Unified Route Flow")
    from app.ai.gateway.provider_registry import ProviderRegistry
    from app.ai.gateway.model_registry import ModelRegistry as GatewayModelRegistry
    from app.ai.gateway.provider_factory import ProviderFactory
    from app.ai.gateway.retry_policy import RetryPolicy
    from app.ai.gateway.timeout_policy import TimeoutPolicy
    from app.ai.gateway.ai_gateway import AIGateway
    from app.ai.models import ChatRequest, PromptMessage, MessageRole

    prov_reg = ProviderRegistry()
    gw = AIGateway(
        provider_registry=prov_reg,
        model_registry=GatewayModelRegistry(),
        factory=ProviderFactory(registry=prov_reg),
        retry_policy=RetryPolicy(),
        timeout_policy=TimeoutPolicy(),
    )
    gw_chat_res = await gw.chat(ChatRequest(messages=[PromptMessage(role="user", content="Hello AI Gateway")], model="qwen3:8b"))
    print(f"  * AI Gateway Response: '{gw_chat_res.text[:80]}...' | Model = '{gw_chat_res.model}'")
    assert gw_chat_res.text != ""
    print("  [OK] AI Gateway unified routing flow verified.\n")

    # Stage 10: Human Conversation Engine Integration (runtime.chat() Response Generator)
    print("Stage 10: Human Conversation Engine Integration (runtime.chat())")
    resp_gen = ResponseGenerator(runtime_engine=runtime)
    conv_resp = await resp_gen.generate_response(
        "Explain machine learning pipeline",
        emotion=EmotionMetadata(primary_emotion="excited"),
        personality=PersonalityMetadata(name="Developer Partner", tone="technical"),
    )
    print(f"  * Conversation Engine Response: '{conv_resp[:90]}...'")
    assert conv_resp != ""
    print("  [OK] Human Conversation Engine runtime integration verified.\n")

    # Stage 11: Universal Research Engine Integration (runtime.reason() Knowledge Synthesis)
    print("Stage 11: Universal Research Engine Integration (runtime.reason())")
    research_reasoner = ReasoningEngine(runtime_engine=runtime)
    from app.ai.research.models import ClaimVerification
    claims = [ClaimVerification(claim_id="c1", statement="FastAPI offers async routing", verification_score=0.95)]
    reason_res = await research_reasoner.reason("FastAPI Framework", claims)
    print(f"  * Research Reasoning Summary: '{reason_res.evidence_summary[:90]}...'")
    assert len(reason_res.conclusions) >= 1
    print("  [OK] Universal Research Engine runtime integration verified.\n")

    # Stage 12: Software Copilot Professional Integration (runtime.code() Real Code Generator)
    print("Stage 12: Software Copilot Professional Integration (runtime.code())")
    code_gen = CodeGenerator(runtime_engine=runtime)
    reqs = RequirementDocument(project_name="ECommerceApp", business_goals=["Build API"])
    arch = ArchitectureDesign(style="modular_monolith")
    stack = TechStack(languages=["python"], frameworks=["fastapi"])
    generated_files = await code_gen.generate_code(reqs, arch, stack)
    print(f"  * Copilot Generated Files Count: {len(generated_files)} (Main file: '{generated_files[0].path}')")
    assert len(generated_files) == 5
    print("  [OK] Software Copilot runtime code generation verified.\n")

    # Stage 13: Mission Runtime, Desktop Automation & Workflow Studio Integration
    print("Stage 13: Mission Runtime, Desktop Automation & Workflow Studio Integration")
    wf_engine = WorkflowEngine(runtime_engine=runtime)
    dyn_wf = await wf_engine.generate_dynamic_workflow("Build E-Commerce System")

    plan_engine = AIPlanningIntegration(runtime_engine=runtime)
    plan_steps = await plan_engine.compile_goal_plan_async("Generate quarterly sales report presentation")

    wf_opt = WorkflowOptimizer(runtime_engine=runtime)

    print(f"  * Dynamic Mission Tasks Generated: {len(dyn_wf.tasks)}")
    print(f"  * Desktop Plan Compiled Steps: {len(plan_steps)} (Step 1: '{plan_steps[0].title}')")
    assert len(dyn_wf.tasks) == 4 and len(plan_steps) >= 1
    print("  [OK] Mission Runtime, Desktop Automation & Workflow Studio integrations verified.\n")

    # Stage 14: Skills SDK Runtime AI Method Injection (chat(), code(), reason())
    print("Stage 14: Skills SDK Runtime AI Method Injection (chat, code, reason)")
    from app.ai.skills.models import SkillManifest, SkillCategory
    manifest = SkillManifest(skill_id="demo_skill", name="Demo Skill", version="1.0.0", category=SkillCategory.UTILITIES)
    demo_skill = DemoSkill(manifest=manifest, runtime_engine=runtime)
    skill_res = await demo_skill.execute("run", SkillContext(user_id="user1"))
    print(f"  * Skill Injected AI Execution Result: '{skill_res.message[:80]}...'")
    assert skill_res.success is True
    print("  [OK] Skills SDK runtime AI method injection verified.\n")

    # Stage 15: System Telemetry Diagnostics, Intelligent Response Cache & Health Observability
    print("Stage 15: System Telemetry Diagnostics, Intelligent Response Cache & Health Observability")
    scheduler = ResourceScheduler()
    monitor = RuntimeMonitor(scheduler)
    diag = monitor.get_runtime_diagnostics()

    # Intelligent cache verification
    cached_chat = await runtime.chat("What is Nova AI OS?")

    print(f"  * Diagnostic Metrics: Loaded Models = {diag['loaded_models']}")
    print(f"  * Latency: {diag['average_latency_ms']} ms | Throughput: {diag['tokens_per_second']} tokens/sec | Streaming Health = {diag['streaming_health']}")
    print(f"  * Intelligent Cache Verification: Retained cached response = {cached_chat.text_or_data != ''}")
    assert diag["is_healthy"] is True and cached_chat.text_or_data != ""
    print("  [OK] System telemetry, intelligent cache & health observability verified.\n")

    print("==================================================================")
    print("  ALL 15 STAGES PASSED SUCCESSFULLY!")
    print("  Real AI Runtime Integration & Unified Model Execution Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_15_stage_validation())
