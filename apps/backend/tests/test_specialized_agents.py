"""Unit tests for the Specialized AI Agents (Enterprise AI Workforce).
"""

import pytest
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.agents.state_machine import AgentStateValue

@pytest.mark.anyio
async def test_specialized_agents_registration():
    """Verifies that all 11 specialized agents are registered in the registry."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    registry = gateway.agents.registry
    
    assert registry.exists("architect") is True
    assert registry.exists("backend") is True
    assert registry.exists("frontend") is True
    assert registry.exists("database") is True
    assert registry.exists("qa") is True
    assert registry.exists("documentation") is True
    assert registry.exists("devops") is True
    assert registry.exists("security") is True
    assert registry.exists("code_reviewer") is True
    assert registry.exists("research") is True
    assert registry.exists("uiux") is True

@pytest.mark.anyio
async def test_specialized_agents_resolution():
    """Verifies that gateway correctly instantiates and retrieves each specialized agent."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)

    arch = await gateway.architect()
    assert arch.metadata.id == "architect"
    assert arch.metadata.type == "architect"
    
    be = await gateway.backend()
    assert be.metadata.id == "backend"
    
    fe = await gateway.frontend()
    assert fe.metadata.id == "frontend"

    db = await gateway.database()
    assert db.metadata.id == "database"

    qa = await gateway.qa()
    assert qa.metadata.id == "qa"

    doc = await gateway.documentation()
    assert doc.metadata.id == "documentation"

    dev = await gateway.devops()
    assert dev.metadata.id == "devops"

    sec = await gateway.security()
    assert sec.metadata.id == "security"

    res = await gateway.research()
    assert res.metadata.id == "research"

    ui = await gateway.uiux()
    assert ui.metadata.id == "uiux"

@pytest.mark.anyio
async def test_specialized_agent_execution():
    """Verifies execution hooks and output formatting states transitions."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    arch = await gateway.architect()
    
    assert arch.state == AgentStateValue.READY
    
    result = await arch.execute({"goal": "Design relational DB schemas"})
    assert result.status == "success"
    assert "diagram" in result.data
    assert arch.state == AgentStateValue.READY
