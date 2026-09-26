"""Native Local-First Semantic Capability Discovery Engine for Nova-AI.

Provides automatic extraction of capabilities from ApplicationAdapters and Registries,
semantic vector indexing using BAAI/bge-small-en-v1.5 (384d) and FAISSVectorStore,
multi-stage retrieval (semantic + lexical + availability ranking), Top-K filtering,
compact schema formatting, and TaskGraph annotation.
"""

from dataclasses import dataclass, field
import json
import math
import os
import re
import threading
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

import structlog

from app.ai.desktop_automation.application_adapter import (
    BaseApplicationAdapter,
    BlenderApplicationAdapter,
)
from app.ai.desktop_automation.photoshop_adapter import PhotoshopApplicationAdapter
from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.desktop_automation.world_state import WorldStateEngine, WorldStateSnapshot
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.faiss_store import FAISSVectorStore
from app.ai.memory.models import MemoryItem, MemoryType, RetrievalResult

logger = structlog.get_logger("capability_discovery")


@dataclass
class DiscoverableCapability:
    """Canonical discovery-oriented representation of a system action or capability."""

    capability_id: str
    name: str
    description: str = ""
    domain: str = "generic"
    application: str = "System"
    action_type: str = "action"
    input_schema: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    risk_level: str = "low"
    required_permissions: List[str] = field(default_factory=list)
    execution_mode: str = "interactive"
    keywords: List[str] = field(default_factory=list)
    semantic_text: str = ""
    examples: List[str] = field(default_factory=list)
    verification_strategy: str = "world_state"
    async_support: bool = False
    is_available: bool = True
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "application": self.application,
            "action_type": self.action_type,
            "input_schema": self.input_schema,
            "prerequisites": self.prerequisites,
            "risk_level": self.risk_level,
            "required_permissions": self.required_permissions,
            "execution_mode": self.execution_mode,
            "keywords": self.keywords,
            "semantic_text": self.semantic_text,
            "examples": self.examples,
            "verification_strategy": self.verification_strategy,
            "async_support": self.async_support,
            "is_available": self.is_available,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiscoverableCapability":
        return cls(
            capability_id=data["capability_id"],
            name=data["name"],
            description=data.get("description", ""),
            domain=data.get("domain", "generic"),
            application=data.get("application", "System"),
            action_type=data.get("action_type", "action"),
            input_schema=data.get("input_schema", {}),
            prerequisites=data.get("prerequisites", []),
            risk_level=data.get("risk_level", "low"),
            required_permissions=data.get("required_permissions", []),
            execution_mode=data.get("execution_mode", "interactive"),
            keywords=data.get("keywords", []),
            semantic_text=data.get("semantic_text", ""),
            examples=data.get("examples", []),
            verification_strategy=data.get("verification_strategy", "world_state"),
            async_support=data.get("async_support", False),
            is_available=data.get("is_available", True),
            embedding=data.get("embedding"),
        )

    def to_compact_summary(self) -> Dict[str, Any]:
        """Generates compact summary representation for Stage 1 LLM prompt injection."""
        summary = {
            "id": self.capability_id,
            "name": self.name,
            "desc": self.description,
            "app": self.application,
        }
        if self.input_schema:
            summary["params"] = list(self.input_schema.keys()) if isinstance(self.input_schema, dict) else str(self.input_schema)
        if self.risk_level != "low":
            summary["risk"] = self.risk_level
        return summary


class CapabilityExtractor:
    """Extracts discoverable capabilities from authoritative ApplicationAdapters and Registries."""

    def __init__(self, security_engine: Optional[SecurityEngine] = None) -> None:
        self.security_engine = security_engine or SecurityEngine()

    def extract_all_capabilities(self) -> List[DiscoverableCapability]:
        """Extracts capabilities from all registered ApplicationAdapters."""
        extracted: List[DiscoverableCapability] = []
        seen_ids: Set[str] = set()

        # 1. Base Desktop & OS Capabilities
        base_adapter = BaseApplicationAdapter("System")
        for act in base_adapter.SUPPORTED_ACTION_TYPES:
            cap_id = f"system:{act}"
            if cap_id in seen_ids:
                continue
            seen_ids.add(cap_id)
            is_sens = self.security_engine.check_approval_required(act)
            act_tokens = set(act.split("_"))
            kw = list(act_tokens) + ["windows", "os", "desktop", "system"]

            if any(k in act_tokens for k in ["screen", "capture", "screenshot"]):
                kw.extend(["screenshot", "snapshot", "screen", "capture", "display", "printscreen"])
            elif any(k in act_tokens for k in ["click", "press", "type", "key"]):
                kw.extend(["mouse", "keyboard", "input", "ui"])

            extracted.append(
                DiscoverableCapability(
                    capability_id=cap_id,
                    name=act,
                    description=f"Desktop OS action: {act.replace('_', ' ')}",
                    domain="windows",
                    application="System",
                    action_type=act,
                    input_schema=base_adapter.get_action_schema(act),
                    risk_level="high" if is_sens else "low",
                    required_permissions=["human_approval"] if is_sens else ["user"],
                    keywords=list(set(kw)),
                    semantic_text=f"Desktop OS capability {act.replace('_', ' ')}: {' '.join(set(kw))}",
                    examples=[f"Perform {act.replace('_', ' ')}"],
                )
            )

        # 2. Blender Actions
        blender_adapter = BlenderApplicationAdapter()
        for act in blender_adapter.BLENDER_STRUCTURED_ACTIONS:
            cap_id = f"blender:{act}"
            if cap_id in seen_ids:
                continue
            seen_ids.add(cap_id)
            is_async = any(k in act for k in ["render", "simulation", "bake", "asset_job"])
            act_tokens = set(act.split("_"))

            kw = list(act_tokens) + ["3d", "cg", "blender"]

            # Token-aware matching for category enrichment (prevents 'obj' in 'object' bug)
            if any(k in act_tokens for k in ["material", "shader", "principled", "bsdf", "texture", "metallic", "roughness"]):
                kw.extend(["material", "metallic", "metal", "metalness", "roughness", "color", "shader", "bsdf", "pbr", "surface", "shading", "principled"])
            if any(k in act_tokens for k in ["modifier", "subdiv", "subsurf", "bevel", "subdivide"]):
                kw.extend(["modifier", "subdivision", "subdivide", "subsurf", "bevel", "mesh", "geometry", "refine"])
            if any(k in act_tokens for k in ["camera", "render", "light", "lighting"]):
                kw.extend(["camera", "render", "rendering", "lighting", "image", "viewport", "scene", "frame", "shot"])
            if any(k in act_tokens for k in ["import", "export", "gltf", "fbx", "stl", "glb"]):
                kw.extend(["import", "export", "gltf", "glb", "fbx", "stl", "asset", "file", "model", "load"])
            elif "obj" in act_tokens:
                kw.extend(["import", "export", "obj", "asset", "file", "model", "load"])

            kw_set = set(kw)
            extracted.append(
                DiscoverableCapability(
                    capability_id=cap_id,
                    name=act,
                    description=f"Blender 3D action: {act.replace('_', ' ')}",
                    domain="blender",
                    application="Blender",
                    action_type=act,
                    input_schema=blender_adapter.get_action_schema(act),
                    risk_level="low",
                    required_permissions=["user"],
                    execution_mode="async_job" if is_async else "interactive",
                    keywords=list(kw_set),
                    semantic_text=f"Blender 3D capability {act.replace('_', ' ')}: {' '.join(kw_set)}",
                    examples=[f"Run {act.replace('_', ' ')} in Blender"],
                    async_support=is_async,
                )
            )

        # 3. Photoshop Actions
        ps_adapter = PhotoshopApplicationAdapter()
        for act in ps_adapter.validator.SUPPORTED_ACTIONS:
            cap_id = f"photoshop:{act}"
            if cap_id in seen_ids:
                continue
            seen_ids.add(cap_id)
            act_tokens = set(act.split("_"))
            extracted.append(
                DiscoverableCapability(
                    capability_id=cap_id,
                    name=act,
                    description=f"Adobe Photoshop image action: {act.replace('_', ' ')}",
                    domain="photoshop",
                    application="Photoshop",
                    action_type=act,
                    input_schema={"action_type": act},
                    risk_level="low",
                    required_permissions=["user"],
                    keywords=list(act_tokens | {"image", "design", "photoshop"}),
                    semantic_text=f"Photoshop capability {act.replace('_', ' ')}: image design document {' '.join(act_tokens)}",
                    examples=[f"Execute {act.replace('_', ' ')} in Photoshop"],
                )
            )

        # 4. Browser & Web Actions
        browser_actions = [
            ("navigate", "Navigate browser to target URL, website, or search query", ["open", "go", "navigate", "website", "url", "web", "browser", "page", "search", "http", "domain", "link"]),
            ("observe_page", "Observe current webpage title, URL, body text, and interactive elements", ["observe", "read", "inspect", "page", "title", "url", "text", "dom", "browser", "content"]),
            ("click_element", "Click a visible web element, link, or button", ["click", "press", "follow", "link", "button", "element", "select", "web", "target"]),
            ("fill_input", "Type text or query into a web input field", ["type", "fill", "input", "enter", "query", "text", "field", "form", "search", "box"]),
            ("submit_form", "Submit active web form or trigger search submission", ["submit", "send", "form", "enter", "query", "search"]),
            ("take_screenshot", "Capture browser page screenshot image", ["screenshot", "snapshot", "capture", "image", "view", "page", "browser"]),
            ("extract_content", "Extract visible text or HTML content from webpage", ["extract", "get", "text", "content", "scrape", "read", "copy", "info"]),
            ("verify_page_state", "Verify webpage title, URL, or text evidence", ["verify", "check", "assert", "validate", "state", "title", "url", "page"]),
        ]
        for act, desc, kw_list in browser_actions:
            cap_id = f"browser:{act}"
            if cap_id in seen_ids:
                continue
            seen_ids.add(cap_id)
            extracted.append(
                DiscoverableCapability(
                    capability_id=cap_id,
                    name=act,
                    description=desc,
                    domain="browser",
                    application="Browser",
                    action_type=act,
                    input_schema={"action_type": act},
                    risk_level="medium" if act in ("fill_input", "click_element") else "low",
                    required_permissions=["user"],
                    keywords=kw_list,
                    semantic_text=f"Browser capability {act}: {desc} {' '.join(kw_list)}",
                    examples=[f"{act.capitalize()} on webpage"],
                )
            )

        # 5. Code & Autonomous Coding Actions
        code_actions = [
            ("understand_repo", "Autonomously inspect repository root, project type, languages, entry points, dependencies, and git state", ["inspect", "understand", "repo", "repository", "architecture", "project", "structure", "languages", "dependencies", "git", "entrypoint", "explain"]),
            ("search_symbol", "Search codebase AST or symbols for class, function, method, or variable definitions", ["search", "find", "symbol", "function", "class", "method", "definition", "ast", "code", "reference"]),
            ("search_text", "Search raw text or regex pattern across project files using local search", ["search", "grep", "find", "pattern", "text", "string", "code", "file", "query"]),
            ("read_file", "Read file contents with targeted line windowing and context management", ["read", "view", "inspect", "file", "source", "code", "content", "lines"]),
            ("write_file", "Safely create or overwrite file with checkpointing and syntax validation", ["write", "create", "file", "save", "code", "source"]),
            ("patch_file", "Apply precise targeted code modification with pre-edit hash check and diff generation", ["edit", "patch", "modify", "update", "refactor", "fix", "code", "file", "change", "add"]),
            ("run_command", "Execute local runtime commands (python, node, npm, ruff, etc.) with security boundary and secret redaction", ["run", "execute", "command", "terminal", "toolchain", "interpreter", "compiler", "process"]),
            ("git_status", "Inspect git working tree, staged changes, branches, and diffs safely", ["git", "status", "diff", "branch", "history", "log", "repo", "vcs"]),
            ("verify_build", "Execute project validation, linting, syntax check, or tests to verify code goals", ["verify", "test", "validate", "build", "check", "lint", "syntax", "goal"]),
        ]
        for act, desc, kw_list in code_actions:
            cap_id = f"code:{act}"
            if cap_id in seen_ids:
                continue
            seen_ids.add(cap_id)
            extracted.append(
                DiscoverableCapability(
                    capability_id=cap_id,
                    name=act,
                    description=desc,
                    domain="code",
                    application="DevelopmentEnvironment",
                    action_type=act,
                    input_schema={"action_type": act},
                    risk_level="medium" if act in ("patch_file", "write_file", "run_command") else "low",
                    required_permissions=["user"],
                    keywords=kw_list,
                    semantic_text=f"Code capability {act}: {desc} {' '.join(kw_list)}",
                    examples=[f"Perform {act.replace('_', ' ')} on codebase"],
                )
            )

        # 6. Research & Scientific Literature Discovery Actions
        research_actions = [
            ("discover_literature", "Search scholarly scientific literature across Crossref, OpenAlex, arXiv, and Europe PMC by query, title, author, or year", ["research", "literature", "paper", "scholarly", "journal", "academic", "crossref", "openalex", "arxiv", "europepmc", "search", "publication", "find"]),
            ("lookup_doi", "Validate DOI syntax, resolve registry metadata via Crossref/OpenAlex, compare title/author agreement, and report discrepancies", ["doi", "validate", "resolve", "registry", "crossref", "openalex", "citation", "verify", "metadata", "mismatch"]),
            ("get_source_metadata", "Retrieve normalized scholarly source record with full-text availability status, provenance, and raw provider metadata", ["source", "metadata", "provenance", "abstract", "authors", "venue", "fulltext", "pdf", "record"]),
        ]
        for act, desc, kw_list in research_actions:
            cap_id = f"research:{act}"
            if cap_id in seen_ids:
                continue
            seen_ids.add(cap_id)
            extracted.append(
                DiscoverableCapability(
                    capability_id=cap_id,
                    name=act,
                    description=desc,
                    domain="research",
                    application="ResearchEngine",
                    action_type=act,
                    input_schema={"action_type": act},
                    risk_level="low",
                    required_permissions=["user"],
                    keywords=kw_list,
                    semantic_text=f"Research capability {act}: {desc} {' '.join(kw_list)}",
                    examples=[f"Execute {act.replace('_', ' ')} for scientific query"],
                )
            )

        logger.info("Extracted capabilities from adapters", total=len(extracted))
        return extracted



class SemanticCapabilityIndex:
    """Vector index managing capability vector embeddings and persistent storage."""

    def __init__(
        self,
        storage_path: str = ".nova/capabilities/",
        embedding_manager: Optional[EmbeddingManager] = None,
    ) -> None:
        self.storage_path = storage_path
        self.meta_file = os.path.join(storage_path, "capabilities_metadata.json")
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.vector_store = FAISSVectorStore(storage_path=storage_path)
        self.capabilities: Dict[str, DiscoverableCapability] = {}
        self.load()

    def load(self) -> None:
        """Loads index metadata from disk."""
        if not os.path.exists(self.meta_file):
            return
        try:
            with open(self.meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for cid, cdict in data.items():
                    self.capabilities[cid] = DiscoverableCapability.from_dict(cdict)
            logger.debug("Loaded capabilities metadata index", count=len(self.capabilities))
        except Exception as e:
            logger.warning("Failed to load capability index metadata", error=str(e))

    def save(self) -> None:
        """Saves capability metadata index to disk."""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            data = {cid: cap.to_dict() for cid, cap in self.capabilities.items()}
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.debug("Saved capability index metadata", count=len(self.capabilities))
        except Exception as e:
            logger.error("Failed to save capability index metadata", error=str(e))

    async def build_index(self, capabilities: List[DiscoverableCapability], force_rebuild: bool = False) -> Dict[str, Any]:
        """Builds or updates vector index for discoverable capabilities."""
        start_t = time.time()
        new_items: List[MemoryItem] = []
        indexed_cnt = 0

        for cap in capabilities:
            cid = cap.capability_id
            needs_embed = force_rebuild or (cid not in self.capabilities) or (not self.capabilities[cid].embedding)

            if needs_embed:
                text_to_embed = cap.semantic_text or f"{cap.name} {cap.description} {' '.join(cap.keywords)}"
                try:
                    embed_vec = await self.embedding_manager.embed_text(text_to_embed)
                    cap.embedding = embed_vec
                except Exception as e:
                    logger.warning("Failed to generate embedding for capability", cap_id=cid, error=str(e))
                    continue

                mem_item = MemoryItem(
                    id=uuid.uuid5(uuid.NAMESPACE_DNS, cid),
                    content=text_to_embed,
                    memory_type=MemoryType.SYSTEM,
                    metadata={"capability_id": cid, "domain": cap.domain, "application": cap.application},
                    embedding=cap.embedding,
                )
                new_items.append(mem_item)
                indexed_cnt += 1

            self.capabilities[cid] = cap

        if new_items:
            await self.vector_store.add(new_items)
            self.save()

        duration = round(time.time() - start_t, 3)
        return {"total_capabilities": len(self.capabilities), "newly_indexed": indexed_cnt, "duration_sec": duration}

    async def search_vector_candidates(self, query_text: str, limit: int = 50) -> List[Tuple[DiscoverableCapability, float]]:
        """Queries local FAISSVectorStore for semantic vector similarity matches."""
        query_vector = await self.embedding_manager.embed_text(query_text)
        results: List[RetrievalResult] = await self.vector_store.search(query_vector, limit=limit, threshold=0.0)

        candidates: List[Tuple[DiscoverableCapability, float]] = []
        for r in results:
            cid = r.metadata.get("capability_id")
            if cid and cid in self.capabilities:
                candidates.append((self.capabilities[cid], r.similarity_score))

        return candidates


@dataclass
class DiscoveryRankingWeights:
    """Configurable weights for multi-stage capability ranking."""

    semantic_weight: float = 0.40
    lexical_weight: float = 0.45
    domain_weight: float = 0.10
    availability_weight: float = 0.05


class CapabilityDiscoveryEngine:
    """Multi-stage retrieval and ranking engine producing Top-K relevant capabilities."""

    STOP_WORDS = {"to", "a", "an", "the", "of", "for", "in", "on", "with", "and", "or", "is", "at", "by", "from", "it", "this", "that"}

    TERM_EQUIVALENTS = {
        "subdivision": {"subdivision", "subdivide", "subsurf"},
        "subdivide": {"subdivision", "subdivide", "subsurf"},
        "metallic": {"metallic", "metal", "metalness"},
        "metal": {"metallic", "metal", "metalness"},
        "gltf": {"gltf", "glb"},
        "glb": {"gltf", "glb"},
        "camera": {"camera", "cameras"},
        "render": {"render", "rendering"},
        "rendering": {"render", "rendering"},
        "screenshot": {"screenshot", "snapshot", "screen_capture", "printscreen"},
    }

    _instance: Optional["CapabilityDiscoveryEngine"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "CapabilityDiscoveryEngine":
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(
        self,
        index: Optional[SemanticCapabilityIndex] = None,
        world_state_engine: Optional[WorldStateEngine] = None,
        weights: Optional[DiscoveryRankingWeights] = None,
    ) -> None:
        self.index = index or SemanticCapabilityIndex()
        self.world_state_engine = world_state_engine or WorldStateEngine.get_instance()
        self.weights = weights or DiscoveryRankingWeights()
        self.extractor = CapabilityExtractor()

    def get_capability(self, capability_id: str) -> Optional[DiscoverableCapability]:
        """Retrieves a capability by ID from the index."""
        return self.index.capabilities.get(capability_id)

    def _normalize_query_for_semantic_search(self, query: str) -> str:
        """Lightweight terminology expansion specifically for semantic vector search."""
        q = query.lower().strip()
        replacements = [
            ("subdivision", "subdivide modifier subsurf"),
            ("subdivide", "subdivide modifier"),
            ("metallic", "metallic metal material principled bsdf"),
            ("metalness", "metallic metal material"),
            ("gltf", "gltf glb import_gltf"),
            ("rendering", "render"),
            ("screenshot", "screen capture screenshot"),
        ]
        for old, new in replacements:
            if old in q and new not in q:
                q = q + " " + new
        return q

    GENERIC_WORDS = {
        "to", "a", "an", "the", "of", "for", "in", "on", "with", "and", "or", "is", "at", "by", "from", "it", "this", "that",
        "make", "add", "create", "set", "get", "do", "run", "perform", "apply", "start", "use", "object", "model", "action"
    }

    def _compute_lexical_score(self, user_goal: str, cap: DiscoverableCapability) -> float:
        """Computes specificity-aware lexical matching score using raw intent tokens."""
        raw_query = user_goal.lower().strip()
        query_words = [w for w in re.findall(r'\b[a-zA-Z0-9_]+\b', raw_query) if w not in self.STOP_WORDS]
        if not query_words:
            return 0.0

        cap_name = cap.name.lower()
        cap_name_tokens = set(cap_name.split("_"))
        cap_keywords = {k.lower() for k in cap.keywords}

        # Exact full capability name or ID match
        if cap_name == raw_query.replace(" ", "_") or cap.capability_id.lower() == raw_query:
            return 1.0

        tech_words = [w for w in query_words if w not in self.GENERIC_WORDS]

        if tech_words:
            tech_name_matches = 0
            tech_kw_matches = 0
            for tw in tech_words:
                equivs = self.TERM_EQUIVALENTS.get(tw, {tw})
                if any(e in cap_name_tokens for e in equivs):
                    tech_name_matches += 1
                elif any(e in cap_keywords for e in equivs):
                    tech_kw_matches += 1

            total_tech = len(tech_words)
            if tech_name_matches == total_tech:
                score = 0.95
            elif tech_name_matches > 0:
                score = 0.60 + (0.25 * (tech_name_matches / total_tech)) + (0.10 * (tech_kw_matches / total_tech))
            elif tech_kw_matches == total_tech:
                score = 0.65
            elif tech_kw_matches > 0:
                score = 0.35 * (tech_kw_matches / total_tech)
            else:
                score = 0.0
        else:
            generic_matches = sum(1 for qw in query_words if qw in cap_name_tokens)
            score = min(0.50, 0.20 * generic_matches)

        # Conflict penalty (e.g. query specifies 'import' but action is 'export')
        if "import" in query_words and "export" in cap_name_tokens:
            score *= 0.3
        elif "export" in query_words and "import" in cap_name_tokens:
            score *= 0.3

        return min(1.0, score)


    async def initialize(self) -> Dict[str, Any]:
        """Auto-extracts capabilities from adapters and builds/synchronizes vector index."""
        caps = self.extractor.extract_all_capabilities()
        return await self.index.build_index(caps, force_rebuild=False)

    async def discover_capabilities_with_scores(
        self,
        user_goal: str,
        domain_filter: Optional[str] = None,
        top_k: int = 8,
        min_score: float = 0.40,
    ) -> List[Dict[str, Any]]:
        """Retrieves Top-K capabilities along with detailed transparent score breakdown."""
        start_t = time.time()

        if not self.index.capabilities:
            await self.initialize()

        sem_query = self._normalize_query_for_semantic_search(user_goal)

        # 1. Semantic Vector Candidate Search
        vector_results = await self.index.search_vector_candidates(sem_query, limit=100)
        vector_scores = {cap.capability_id: sem_score for cap, sem_score in vector_results}

        # Candidate pool
        candidates = [(cap, vector_scores.get(cap.capability_id, 0.0)) for cap in self.index.capabilities.values()]

        # 2. Get WorldState for Dynamic Availability
        snapshot: WorldStateSnapshot = self.world_state_engine.refresh()
        active_app = (snapshot.application.active_app_name.value or "").lower()

        # Inferred domain
        raw_words = set(user_goal.lower().replace("_", " ").split())
        inferred_domain = None
        if any(w in raw_words for w in ["mesh", "3d", "render", "camera", "modifier", "subdivision", "material", "metallic", "gltf", "fbx", "obj"]):
            inferred_domain = "blender"
        elif any(w in raw_words for w in ["screenshot", "window", "terminal", "desktop"]):
            inferred_domain = "windows"
        elif any(w in raw_words for w in ["code", "python", "bug", "function", "endpoint", "repo", "architecture", "refactor", "fix", "class", "file", "build", "test", "patch", "git"]):
            inferred_domain = "code"


        scored_details: List[Dict[str, Any]] = []

        for cap, sem_score in candidates:
            if domain_filter and cap.domain.lower() != domain_filter.lower():
                continue

            lex_score = self._compute_lexical_score(user_goal, cap)

            # Domain Relevance Score
            domain_score = 0.5
            if inferred_domain and cap.domain.lower() == inferred_domain:
                domain_score = 1.0
            elif cap.domain.lower() == "blender":
                domain_score = 0.7

            # Availability Score
            avail_score = 1.0
            if cap.application.lower() in active_app:
                avail_score = 1.0
            elif cap.application.lower() != "system":
                avail_score = 0.8

            final_score = (
                (sem_score * self.weights.semantic_weight)
                + (lex_score * self.weights.lexical_weight)
                + (domain_score * self.weights.domain_weight)
                + (avail_score * self.weights.availability_weight)
            )

            if final_score >= min_score:
                scored_details.append(
                    {
                        "capability": cap,
                        "final_score": final_score,
                        "semantic_score": sem_score,
                        "lexical_score": lex_score,
                        "domain_score": domain_score,
                        "availability_score": avail_score,
                    }
                )

        scored_details.sort(key=lambda x: x["final_score"], reverse=True)
        selected = scored_details[:top_k]

        logger.info(
            "Capability discovery with scores completed",
            goal=user_goal,
            selected_count=len(selected),
            duration_ms=round((time.time() - start_t) * 1000, 2),
        )
        return selected

    async def discover_capabilities(
        self,
        user_goal: str = "",
        domain_filter: Optional[str] = None,
        top_k: int = 8,
        min_score: float = 0.40,
        query: Optional[str] = None,
    ) -> List[DiscoverableCapability]:
        """Retrieves and ranks Top-K capabilities matching user goal."""
        target_goal = query or user_goal
        scored_details = await self.discover_capabilities_with_scores(
            user_goal=target_goal,
            domain_filter=domain_filter,
            top_k=top_k,
            min_score=min_score,
        )
        return [item["capability"] for item in scored_details]

    def discover_capabilities_sync(
        self,
        user_goal: str = "",
        domain_filter: Optional[str] = None,
        top_k: int = 8,
        min_score: float = 0.40,
        query: Optional[str] = None,
    ) -> List[DiscoverableCapability]:
        """Synchronous wrapper for capability discovery."""
        target_goal = query or user_goal
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            def _run():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(
                        self.discover_capabilities(target_goal, domain_filter, top_k, min_score)
                    )
                finally:
                    new_loop.close()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(_run).result()
        else:
            return asyncio.run(self.discover_capabilities(target_goal, domain_filter, top_k, min_score))

    def annotate_task_graph_node(self, node_metadata: Dict[str, Any], capability: DiscoverableCapability) -> None:
        """Annotates TaskGraph ACTION node metadata with capability traceability fields."""
        node_metadata["capability_id"] = capability.capability_id
        node_metadata["capability_domain"] = capability.domain
        node_metadata["capability_name"] = capability.name
        node_metadata["capability_risk_level"] = capability.risk_level


class CompactSchemaFormatter:
    """Formats discovered capabilities into compact LLM prompt context summaries."""

    @staticmethod
    def format_compact_schemas(capabilities: List[DiscoverableCapability]) -> str:
        """Stage 1: Generates compact JSON summary context string for LLM system prompt."""
        summaries = [cap.to_compact_summary() for cap in capabilities]
        return json.dumps(summaries, indent=2)

    @staticmethod
    def format_expanded_schema(capability: DiscoverableCapability) -> str:
        """Stage 2: Generates full JSON parameter schema for on-demand expansion."""
        return json.dumps(capability.to_dict(), indent=2)

    @staticmethod
    def estimate_token_count(text: str) -> int:
        """Heuristic estimation of token count (~4 characters per token)."""
        return math.ceil(len(text) / 4)
