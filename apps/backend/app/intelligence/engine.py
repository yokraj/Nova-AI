"""Universal Intelligence Engine (Nova Brain) Master Orchestrator Module.

Unifies all sub-engines (Planner, Reasoner, Knowledge, Memory, Routers, Verification,
Reflection, Decision, Learning, Response Generator, Conversation) into a cohesive,
high-performance, local-first AGI-grade core for the Nova AI Operating System.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional
import structlog

from app.intelligence.config import IntelligenceConfig
from app.intelligence.exceptions import IntelligenceError
from app.intelligence.prompt_manager import PromptManager
from app.intelligence.personality import PersonalityEngine
from app.intelligence.model_router import ModelRouter
from app.intelligence.tool_router import ToolRouter
from app.intelligence.agent_router import AgentRouter
from app.intelligence.intent_detection import IntentDetector
from app.intelligence.task_decomposer import TaskDecomposer
from app.intelligence.planner import TaskPlanner
from app.intelligence.reasoner import ReasoningEngine
from app.intelligence.knowledge import KnowledgeEngine
from app.intelligence.memory import MemoryEngine
from app.intelligence.context import ContextManager
from app.intelligence.verification import VerificationEngine
from app.intelligence.reflection import ReflectionEngine
from app.intelligence.decision_engine import DecisionEngine
from app.intelligence.learning import LearningEngine
from app.intelligence.response_generator import ResponseGenerator
from app.intelligence.conversation import ConversationEngine

logger = structlog.get_logger(__name__)


class UniversalIntelligenceEngine:
    """Master Intelligence Layer for Nova AI Operating System."""

    def __init__(self, config: Optional[IntelligenceConfig] = None) -> None:
        self.config = config or IntelligenceConfig()
        
        # Sub-Engines Initialization
        self.prompt_manager = PromptManager()
        self.personality_engine = PersonalityEngine()
        self.model_router = ModelRouter(config=self.config)
        self.tool_router = ToolRouter()
        self.agent_router = AgentRouter()
        self.intent_detector = IntentDetector()
        self.task_decomposer = TaskDecomposer()
        self.planner = TaskPlanner(
            tool_router=self.tool_router,
            agent_router=self.agent_router,
            task_decomposer=self.task_decomposer,
        )
        self.reasoner = ReasoningEngine()
        self.knowledge_engine = KnowledgeEngine()
        self.memory_engine = MemoryEngine()
        self.context_manager = ContextManager(config=self.config)
        self.verification_engine = VerificationEngine()
        self.reflection_engine = ReflectionEngine()
        self.decision_engine = DecisionEngine()
        self.learning_engine = LearningEngine()
        self.response_generator = ResponseGenerator(personality_engine=self.personality_engine)
        self.conversation_engine = ConversationEngine(
            intent_detector=self.intent_detector,
            memory_engine=self.memory_engine,
            context_manager=self.context_manager,
            personality_engine=self.personality_engine,
        )

        logger.info("universal_intelligence_engine_initialized", default_model=self.config.default_model)

    async def process_request(
        self, prompt: str, conversation_id: str = "default", **kwargs: Any
    ) -> Dict[str, Any]:
        """Main entry point for processing queries, conversations, planning, and multi-domain tasks."""
        logger.info("processing_intelligence_request", conversation_id=conversation_id, prompt_len=len(prompt))

        try:
            # 1. Evaluate Decision Requirements
            history = await self.memory_engine.get_recent_conversation_history(conversation_id)
            decisions = self.decision_engine.evaluate_request(prompt, len(history))

            # 2. Intent Detection
            intent = self.intent_detector.detect_intent(prompt)

            # 3. Route to Planning if Complex
            plan: Optional[Dict[str, Any]] = None
            if decisions.get("need_multiple_agents") or intent.get("category") == "multi_step_planning":
                plan = self.planner.create_plan(prompt)

            # 4. Knowledge Retrieval if Needed
            knowledge_data: Optional[Dict[str, Any]] = None
            if decisions.get("need_rag"):
                knowledge_data = await self.knowledge_engine.retrieve_hybrid_knowledge(prompt)

            # 5. Logical Reasoning if Needed
            reasoning_data: Optional[Dict[str, Any]] = None
            if decisions.get("need_coding") or intent.get("category") == "deep_reasoning":
                reasoning_data = await self.reasoner.step_by_step_reasoning(prompt)

            # 6. Conversation Processing & Draft Response Generation
            turn_result = await self.conversation_engine.process_turn(prompt, conversation_id)
            draft_response = turn_result["response"]

            # 7. Self-Verification & Hallucination Check
            verification = None
            if self.config.enable_self_verification:
                grounding = knowledge_data.get("context_summary") if knowledge_data else None
                verification = await self.verification_engine.verify_output(draft_response, grounding)

            # 8. Pre-response Reflection Loop
            final_response = draft_response
            reflection = None
            if self.config.enable_reflection:
                reflection = await self.reflection_engine.reflect_and_refine(draft_response, prompt)
                final_response = reflection["refined_response"]

            # Format final output
            formatted_output = self.response_generator.format_response(final_response, domain=intent["category"])

            # 9. Update Adaptive Learning Observation
            await self.learning_engine.observe_user_action("query_processed", {"intent": intent["category"]})

            return {
                "response": formatted_output,
                "conversation_id": conversation_id,
                "intent": intent,
                "decisions": decisions,
                "plan": plan,
                "knowledge": knowledge_data,
                "reasoning": reasoning_data,
                "verification": verification,
                "reflection": reflection,
                "model_info": self.model_router.select_model(intent["category"]),
            }
        except Exception as exc:
            logger.error("intelligence_request_failed", error=str(exc))
            raise IntelligenceError(f"Failed to process intelligence request: {exc}") from exc

    async def stream_request(
        self, prompt: str, conversation_id: str = "default"
    ) -> AsyncGenerator[str, None]:
        """Streams response tokens asynchronously for interactive interfaces."""
        result = await self.process_request(prompt, conversation_id=conversation_id)
        full_text = result["response"]
        async for chunk in self.response_generator.stream_response_tokens(full_text):
            yield chunk
