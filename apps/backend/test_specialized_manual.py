"""Manual Validation script for Specialized AI Agents.
"""

import asyncio
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.planner.models import PlanningRequest

async def main():
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    passed = 0
    total = 12

    # 1. Architect Agent
    try:
        agent = await gateway.architect()
        res = await agent.execute("Design DB table migrations")
        assert res.status == "success"
        print("Architect Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"Architect Agent\nFAIL ({str(err)})")

    # 2. Backend Agent
    try:
        agent = await gateway.backend()
        res = await agent.execute("Generate auth router")
        assert res.status == "success"
        print("Backend Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"Backend Agent\nFAIL ({str(err)})")

    # 3. Frontend Agent
    try:
        agent = await gateway.frontend()
        res = await agent.execute("Build layout pages")
        assert res.status == "success"
        print("Frontend Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"Frontend Agent\nFAIL ({str(err)})")

    # 4. Database Agent
    try:
        agent = await gateway.database()
        res = await agent.execute("Optimize Alembic indices")
        assert res.status == "success"
        print("Database Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"Database Agent\nFAIL ({str(err)})")

    # 5. QA Agent
    try:
        agent = await gateway.qa()
        res = await agent.execute("Run pytest check")
        assert res.status == "success"
        print("QA Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"QA Agent\nFAIL ({str(err)})")

    # 6. Documentation Agent
    try:
        agent = await gateway.documentation()
        res = await agent.execute("Generate OpenAPI reference doc")
        assert res.status == "success"
        print("Documentation Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"Documentation Agent\nFAIL ({str(err)})")

    # 7. DevOps Agent
    try:
        agent = await gateway.devops()
        res = await agent.execute("Write deployment workflow config")
        assert res.status == "success"
        print("DevOps Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"DevOps Agent\nFAIL ({str(err)})")

    # 8. Security Agent
    try:
        agent = await gateway.security()
        res = await agent.execute("Scan dependency vulnerabilities list")
        assert res.status == "success"
        print("Security Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"Security Agent\nFAIL ({str(err)})")

    # 9. Research Agent
    try:
        agent = await gateway.research()
        res = await agent.execute("Audit architecture comparison reports")
        assert res.status == "success"
        print("Research Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"Research Agent\nFAIL ({str(err)})")

    # 10. UI/UX Agent
    try:
        agent = await gateway.uiux()
        res = await agent.execute("Draw branding system guidelines")
        assert res.status == "success"
        print("UI/UX Agent\nPASS")
        passed += 1
    except Exception as err:
        print(f"UI/UX Agent\nFAIL ({str(err)})")

    # 11. Planner Integration
    try:
        # The planner should auto-assign the Database Agent for db capability task
        request = PlanningRequest(request_id="manual_plan_workforce", goal="Decompose CRM table schema migrations and setup postgres index databases")
        response = await gateway.plan(request)
        assert response.status == "success"

        has_db_agent = False
        for node in response.dependency_graph.nodes.values():
            if node.assignment and node.assignment.agent_id == "database":
                has_db_agent = True
                break
        assert has_db_agent is True
        print("Planner Integration\nPASS")
        passed += 1
    except Exception as err:
        print(f"Planner Integration\nFAIL ({str(err)})")

    # 12. Gateway Integration
    try:
        assert hasattr(gateway, "architect")
        assert hasattr(gateway, "backend")
        assert hasattr(gateway, "frontend")
        print("Gateway Integration\nPASS")
        passed += 1
    except Exception as err:
        print(f"Gateway Integration\nFAIL ({str(err)})")

    print(f"\n{passed} / {total} PASS")

if __name__ == "__main__":
    asyncio.run(main())
