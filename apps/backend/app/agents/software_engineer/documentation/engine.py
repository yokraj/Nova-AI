"""Main DocumentationEngine coordinating planners, renderers, search and templates.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.documentation.interfaces import DocumentationEngine
from app.agents.software_engineer.documentation.planner import ProjectDocumentationPlanner
from app.agents.software_engineer.documentation.context_builder import DocumentationContextBuilder
from app.agents.software_engineer.documentation.prompt_builder import DocumentationPromptBuilder
from app.agents.software_engineer.documentation.analyzer import WorkspaceDocumentationAnalyzer
from app.agents.software_engineer.documentation.architecture_generator import SystemArchitectureGenerator
from app.agents.software_engineer.documentation.api_documenter import FastAPIDocumenter
from app.agents.software_engineer.documentation.code_documenter import WorkspaceCodeDocumenter
from app.agents.software_engineer.documentation.diagram_generator import MermaidDiagramGenerator
from app.agents.software_engineer.documentation.knowledge_builder import LocalKnowledgeBuilder
from app.agents.software_engineer.documentation.knowledge_index import LocalKnowledgeIndexer
from app.agents.software_engineer.documentation.search import LocalDocumentationSearcher
from app.agents.software_engineer.documentation.sync import DocumentationSyncEngine
from app.agents.software_engineer.documentation.version_tracker import DocumentationVersionTracker
from app.agents.software_engineer.documentation.template_engine import WorkspaceTemplateEngine
from app.agents.software_engineer.documentation.markdown_renderer import TechnicalMarkdownRenderer
from app.agents.software_engineer.documentation.html_renderer import TechnicalHTMLRenderer
from app.agents.software_engineer.documentation.pdf_renderer import TechnicalPDFRenderer
from app.agents.software_engineer.documentation.report_generator import ProjectReportGenerator
from app.agents.software_engineer.documentation.cache import DocumentationCache
from app.agents.software_engineer.documentation.exceptions import GenerationError
from app.agents.software_engineer.documentation.models import (
    DocumentationPlan,
    DocumentationReport,
    DocumentationRequest,
    ReadmeDocument,
)
from app.agents.software_engineer.generator.utils import extract_code_block
from app.ai.models import ChatRequest


class LocalDocumentationEngine(DocumentationEngine):
    """Main orchestrator running the documentation and knowledge pipelines."""

    def __init__(self, gateway: Any, workspace_root: Optional[str] = None) -> None:
        """Initializes LocalDocumentationEngine.

        Args:
            gateway: Active AI Gateway.
            workspace_root: Workspace root path.
        """
        self.gateway = gateway
        self.workspace_root = workspace_root or os.getcwd()

        self.planner = ProjectDocumentationPlanner()
        self.context_builder = DocumentationContextBuilder()
        self.prompt_builder = DocumentationPromptBuilder()
        self.analyzer = WorkspaceDocumentationAnalyzer()
        self.architecture_generator = SystemArchitectureGenerator()
        self.api_documenter = FastAPIDocumenter()
        self.code_documenter = WorkspaceCodeDocumenter()
        self.diagram_generator = MermaidDiagramGenerator()
        self.knowledge_builder = LocalKnowledgeBuilder()
        self.knowledge_indexer = LocalKnowledgeIndexer()
        self.searcher = LocalDocumentationSearcher()
        self.sync_engine = DocumentationSyncEngine()
        self.version_tracker = DocumentationVersionTracker()
        self.template_engine = WorkspaceTemplateEngine()
        self.md_renderer = TechnicalMarkdownRenderer()
        self.html_renderer = TechnicalHTMLRenderer()
        self.pdf_renderer = TechnicalPDFRenderer()
        self.report_generator = ProjectReportGenerator()

        # Local cache path
        nova_dir = os.path.join(self.workspace_root, ".nova", "documentation")
        self.cache = DocumentationCache(os.path.join(nova_dir, "doc_cache.json"))

    def _get_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _resolve_model(self, request: DocumentationRequest) -> str:
        model_name = request.model_override
        if not model_name and self.gateway and hasattr(self.gateway, "model_registry"):
            model_name = self.gateway.model_registry.default_model()
        return model_name or "llama3"

    async def execute_documentation_pipeline(
        self, request: DocumentationRequest
    ) -> DocumentationReport:
        """Orchestrates full scanning, plan mapping, and LLM drafting.

        Args:
            request: Active request settings.

        Returns:
            DocumentationReport.
        """
        prompt_hash = self._get_hash(request.prompt)

        # 1. Check cache
        cached = self.cache.get(prompt_hash)
        if cached:
            try:
                return DocumentationReport.model_validate(cached)
            except Exception:
                pass

        # 2. Build Context & Decompose checklist plan
        context = self.context_builder.build_context(request, self.workspace_root)
        plan = self.planner.plan_documentation(request, context)

        # 3. Resolve dynamic coding model
        model_name = self._resolve_model(request)

        # 4. Generate README using Template Engine and AI Model
        readme_params = {
            "project_name": "Nova AI",
            "description": "Enterprise Agent SDK Architecture.",
            "install_steps": "uv sync",
        }
        raw_readme_tpl = self.template_engine.render_template("readme", readme_params)

        if not self.gateway:
            readme_text = raw_readme_tpl
        else:
            prompt_pkg = self.prompt_builder.build_prompt(request, context, f"Generate README from template: {raw_readme_tpl}")
            chat_req = ChatRequest(
                messages=prompt_pkg.messages,
                model=model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            try:
                chat_res = await self.gateway.chat(chat_req)
                readme_text = chat_res.message.content
            except Exception as e:
                raise GenerationError(f"Local model invocation failed: {str(e)}") from e

        # 5. Extract components architecture Mermaid diagrams
        arch_doc = self.architecture_generator.generate_architecture(self.workspace_root)

        # 6. Gather API Router routes details
        api_routes = self.api_documenter.document_api(self.workspace_root, "app/api/v1/endpoints.py")

        # 7. Render outputs (Markdown, HTML, PDF)
        sections = {
            "README": readme_text,
            "Architecture Design": f"Mermaid layout:\n```mermaid\n{arch_doc.mermaid_diagram}\n```",
            "API Summary": f"Endpoints documented: {len(api_routes)}",
        }
        markdown_out = self.md_renderer.render_markdown(sections)
        html_out = self.html_renderer.render_html("Nova AI Docs", markdown_out)
        pdf_out = self.pdf_renderer.render_to_pdf(markdown_out)

        # 8. Index Knowledge Base
        k_entries = self.knowledge_builder.build_knowledge(self.workspace_root)
        k_index = self.knowledge_indexer.index_knowledge(k_entries)

        # 9. Track Version
        self.version_tracker.track_version("readme", "README.md", readme_text)

        # 10. Compile final report
        undocumented = self.analyzer.find_undocumented_symbols(self.workspace_root)
        report = self.report_generator.generate_report(plan, markdown_out)

        # Cache final report payload
        self.cache.set(prompt_hash, report.model_dump())

        return report
