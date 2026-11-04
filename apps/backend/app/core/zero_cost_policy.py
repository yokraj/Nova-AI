"""Nova AI Centralized Zero-Cost Policy Enforcement Module.

Enforces a permanent local-first, zero-financial-cost architecture:
- 100% Free and open-source models (Ollama local inference).
- Prohibits paid APIs, commercial LLM subscriptions, and cloud provider fallbacks.
- Guarantees offline local speech processing as default.
- Prevents silent activation of online services.
"""

from typing import Any, Dict, List, Set
import structlog

logger = structlog.get_logger("zero_cost_policy")

# Supported and authorized zero-cost local providers
PERMITTED_LOCAL_LLM_PROVIDERS: Set[str] = {
    "ollama",
    "local",
    "llamacpp",
    "llama.cpp",
}

# Strictly prohibited commercial cloud providers
PROHIBITED_COMMERCIAL_PROVIDERS: Set[str] = {
    "openai",
    "anthropic",
    "gemini",
    "google",
    "cohere",
    "mistral-cloud",
    "azure-openai",
    "bedrock",
    "groq",
    "together",
    "deepgram",
    "elevenlabs",
}

# Optional free public services (No account, no billing, free open access)
PERMITTED_OPTIONAL_ONLINE_SERVICES: Set[str] = {
    "edge-tts",        # Microsoft Edge Read Aloud public endpoint
    "arxiv",           # Cornell University Open Access
    "europe_pmc",      # EMBL-EBI Open Access
    "crossref",        # Open DOI metadata
    "openalex",        # Open scholarly catalog
}


class ZeroCostPolicyViolation(PermissionError):
    """Raised when an operation attempts to activate a paid or prohibited provider."""
    pass


class ZeroCostPolicy:
    """Centralized enforcement and validation engine for Zero-Cost Compliance."""

    @staticmethod
    def assert_llm_provider_allowed(provider_name: str) -> None:
        """Validates that requested LLM provider is permitted under Zero-Cost Policy.

        Args:
            provider_name: The requested provider identifier.

        Raises:
            ZeroCostPolicyViolation: If the provider is commercial or unauthorized.
        """
        clean_name = (provider_name or "").lower().strip()
        if clean_name in PROHIBITED_COMMERCIAL_PROVIDERS:
            logger.error("zero_cost_violation_blocked", provider=clean_name)
            raise ZeroCostPolicyViolation(
                f"Provider '{clean_name}' is permanently blocked under the Nova AI Zero-Cost Policy. "
                f"Commercial AI APIs and paid subscriptions are strictly prohibited. "
                f"Please use local Ollama inference ('ollama')."
            )

        if clean_name not in PERMITTED_LOCAL_LLM_PROVIDERS:
            logger.warning("unrecognized_provider_rejected", provider=clean_name)
            raise ZeroCostPolicyViolation(
                f"Provider '{clean_name}' is not an authorized local zero-cost provider. "
                f"Authorized local providers: {sorted(list(PERMITTED_LOCAL_LLM_PROVIDERS))}."
            )

    @staticmethod
    def is_provider_allowed(provider_name: str) -> bool:
        """Non-raising check whether a provider is authorized."""
        clean_name = (provider_name or "").lower().strip()
        return clean_name in PERMITTED_LOCAL_LLM_PROVIDERS

    @staticmethod
    def get_policy_summary() -> Dict[str, Any]:
        """Returns the active zero-cost policy parameters for reporting and telemetry."""
        return {
            "policy_active": True,
            "policy_document": "ZERO_COST_DEVELOPMENT_POLICY.md",
            "enforced_llm_provider": "ollama",
            "offline_voice_preferred": True,
            "online_tts_policy": "explicit_opt_in_only",
            "commercial_fallbacks_allowed": False,
            "permitted_local_providers": sorted(list(PERMITTED_LOCAL_LLM_PROVIDERS)),
            "prohibited_commercial_providers": sorted(list(PROHIBITED_COMMERCIAL_PROVIDERS)),
            "permitted_optional_online_services": sorted(list(PERMITTED_OPTIONAL_ONLINE_SERVICES)),
        }

