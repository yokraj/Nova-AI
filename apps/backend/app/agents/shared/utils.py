"""Shared utilities helper registering specialized agents descriptors.
"""

import structlog
from app.ai.agents.models import AgentDescriptor, AgentMetadata, AgentCapability

logger = structlog.get_logger("shared_agents_utils")

def register_all_specialized_agents(registry) -> None:
    """Pre-registers the 11 specialized workforce agent blueprints in the registry."""
    
    agents_blueprints = [
        # 1. Architect Agent
        ("architect", "Architect Agent", "architect", [
            ("system_design", "Design systems architecture"),
            ("architecture", "Create architectural templates"),
            ("api_design", "Define API routes"),
            ("database_design", "Design DB schemas"),
            ("planning", "Plan execution flows"),
            ("review", "Review architecture")
        ]),
        # 2. Backend Agent
        ("backend", "Backend Agent", "backend", [
            ("python", "Write python backend code"),
            ("fastapi", "Build fastapi backends"),
            ("sql", "Write database queries"),
            ("api", "Expose endpoint structures"),
            ("backend", "Build server side elements"),
            ("security", "Enforce auth controls")
        ]),
        # 3. Frontend Agent
        ("frontend", "Frontend Agent", "frontend", [
            ("react", "Build React frontend code"),
            ("typescript", "Write typescript layout parameters"),
            ("css", "Apply vanilla styling rules"),
            ("tailwind", "Apply tailwind utility selectors"),
            ("frontend", "Assemble client side layouts"),
            ("ui", "Produce web dashboards interface")
        ]),
        # 4. Database Agent
        ("database", "Database Agent", "database", [
            ("postgres", "Create postgres schemas"),
            ("mysql", "Create mysql schemas"),
            ("redis", "Configure temporal caches"),
            ("migration", "Build database migrations templates"),
            ("optimization", "Optimize query indexes")
        ]),
        # 5. QA Agent
        ("qa", "QA Agent", "qa", [
            ("testing", "Write integration tests specs"),
            ("pytest", "Run pytest suites check"),
            ("automation", "Validate selenium automations"),
            ("qa", "Assert quality validation parameters")
        ]),
        # 6. Documentation Agent
        ("documentation", "Documentation Agent", "documentation", [
            ("documentation", "Assemble documentation guides"),
            ("markdown", "Format markdown reports"),
            ("openapi", "Write openapi yaml schema specs"),
            ("readme", "Compile workspace readme guidelines")
        ]),
        # 7. DevOps Agent
        ("devops", "DevOps Agent", "devops", [
            ("docker", "Assemble Dockerfiles"),
            ("github", "Write Github Actions pipeline workflows"),
            ("deployment", "Run setup deployment scripts"),
            ("devops", "Orchestrate pipeline steps"),
            ("linux", "Execute bash script diagnostics")
        ]),
        # 8. Security Agent
        ("security", "Security Agent", "security", [
            ("security", "Conduct vulnerability scans"),
            ("owasp", "Assert owasp security guidelines"),
            ("jwt", "Verify auth token signatures"),
            ("audit", "Audit dependency scans checks")
        ]),
        # 9. Code Reviewer Agent
        ("code_reviewer", "Code Reviewer Agent", "code_reviewer", [
            ("review", "Conduct pull request audits"),
            ("refactor", "Suggest code refactoring paths"),
            ("quality", "Assert clean coding conventions"),
            ("architecture", "Review structure conventions")
        ]),
        # 10. Research Agent
        ("research", "Research Agent", "research", [
            ("research", "Analyze academic preprints"),
            ("analysis", "Compare constraints limits"),
            ("documentation", "Search technical manual docs"),
            ("comparison", "Resolve library comparisons matrices")
        ]),
        # 11. UI/UX Agent
        ("uiux", "UI/UX Agent", "uiux", [
            ("ui", "Design layout screens"),
            ("ux", "Verify navigation flows usability"),
            ("figma", "Export figma layout parameters"),
            ("design", "Establish branding design systems")
        ])
    ]

    for id_, name, type_, capabilities in agents_blueprints:
        if registry.exists(id_):
            continue

        meta = AgentMetadata(
            id=id_,
            name=name,
            type=type_,
            capabilities=[
                AgentCapability(name=cap_name, description=cap_desc)
                for cap_name, cap_desc in capabilities
            ],
            permissions=["Filesystem", "Developer"]
        )
        class_names = {
            "architect": "ArchitectAgent",
            "backend": "BackendAgent",
            "frontend": "FrontendAgent",
            "database": "DatabaseAgent",
            "qa": "QAAgent",
            "documentation": "DocumentationAgent",
            "devops": "DevOpsAgent",
            "security": "SecurityAgent",
            "code_reviewer": "CodeReviewerAgent",
            "research": "ResearchAgent",
            "uiux": "UIUXAgent"
        }
        class_name = class_names[id_]
        descriptor = AgentDescriptor(
            class_path=f"app.agents.{id_}.agent.{class_name}",
            dependencies=[]
        )

        try:
            registry.register(descriptor, meta)
            logger.info("Auto-registered workforce agent blueprint", agent_id=id_, class_path=descriptor.class_path)
        except Exception as err:
            logger.warning("Workforce agent auto-registration skipped", agent_id=id_, error=str(err))
