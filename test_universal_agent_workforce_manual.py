"""20-Stage Comprehensive Manual Validation Script for M3.4.20 Universal Agent Workforce, Autonomous AI Company & Multi-Agent Collaboration Platform.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps/backend")))


async def run_20_stage_validation():
    print("==================================================================")
    print("M3.4.20 – Universal Agent Workforce, Autonomous AI Company & Multi-Agent Platform")
    print("==================================================================\n")

    # Stage 1: Workforce Package Init & PEP 562 Lazy Loader
    print("Stage 1: Workforce Package Init & PEP 562 Lazy Loader")
    from app.ai.agents import WorkforceConfiguration, UniversalAgentWorkforceEngine
    config = WorkforceConfiguration()
    print(f"  * Workforce Name: '{config.workforce_name}' v{config.version} | Local-First = {config.local_first}")
    assert config.enabled is True
    print("  [OK] Workforce package init & lazy loader verified.\n")

    # Stage 2: Universal Workforce Engine Facade & Health Snapshot
    print("Stage 2: Universal Workforce Engine Facade & Health Snapshot")
    engine = UniversalAgentWorkforceEngine()
    health = engine.get_workforce_health()
    print(f"  * Company Status: '{health.status}' | Registered Agents: {health.total_registered_agents} across {health.divisions_count} Divisions")
    assert health.is_healthy is True and health.total_registered_agents == 67
    print("  [OK] Universal Workforce Engine facade verified.\n")

    # Stage 3: Phase 1 Executive Division (6 Agents)
    print("Stage 3: Phase 1 Executive Division (6 Agents)")
    from app.ai.agents.divisions.executive import ExecutiveDivision
    exec_agents = ExecutiveDivision.get_agents()
    print(f"  * Executive Agents Count: {len(exec_agents)} (Roles: {[a.name for a in exec_agents[:3]]})")
    assert len(exec_agents) == 6
    print("  [OK] Executive Division verified.\n")

    # Stage 4: Phase 2 Engineering Division (15 Agents)
    print("Stage 4: Phase 2 Engineering Division (15 Agents)")
    from app.ai.agents.divisions.engineering import EngineeringDivision
    eng_agents = EngineeringDivision.get_agents()
    print(f"  * Engineering Agents Count: {len(eng_agents)} (Roles: {[a.name for a in eng_agents[:4]]})")
    assert len(eng_agents) == 15
    print("  [OK] Engineering Division verified.\n")

    # Stage 5: Phase 3 Research Division (8 Agents)
    print("Stage 5: Phase 3 Research Division (8 Agents)")
    from app.ai.agents.divisions.research import ResearchDivision
    res_agents = ResearchDivision.get_agents()
    print(f"  * Research Agents Count: {len(res_agents)} (Roles: {[a.name for a in res_agents[:3]]})")
    assert len(res_agents) == 8
    print("  [OK] Research Division verified.\n")

    # Stage 6: Phase 4 Creative Division (7 Agents)
    print("Stage 6: Phase 4 Creative Division (7 Agents)")
    from app.ai.agents.divisions.creative import CreativeDivision
    creat_agents = CreativeDivision.get_agents()
    print(f"  * Creative Agents Count: {len(creat_agents)} (Roles: {[a.name for a in creat_agents[:3]]})")
    assert len(creat_agents) == 7
    print("  [OK] Creative Division verified.\n")

    # Stage 7: Phase 5 Business Division (8 Agents)
    print("Stage 7: Phase 5 Business Division (8 Agents)")
    from app.ai.agents.divisions.business import BusinessDivision
    biz_agents = BusinessDivision.get_agents()
    print(f"  * Business Agents Count: {len(biz_agents)} (Roles: {[a.name for a in biz_agents[:4]]})")
    assert len(biz_agents) == 8
    print("  [OK] Business Division verified.\n")

    # Stage 8: Phase 6 Automation Division (6 Agents)
    print("Stage 8: Phase 6 Automation Division (6 Agents)")
    from app.ai.agents.divisions.automation import AutomationDivision
    auto_agents = AutomationDivision.get_agents()
    print(f"  * Automation Agents Count: {len(auto_agents)} (Roles: {[a.name for a in auto_agents[:3]]})")
    assert len(auto_agents) == 6
    print("  [OK] Automation Division verified.\n")

    # Stage 9: Phase 7 Infrastructure Division (7 Agents)
    print("Stage 9: Phase 7 Infrastructure Division (7 Agents)")
    from app.ai.agents.divisions.infrastructure import InfrastructureDivision
    infra_agents = InfrastructureDivision.get_agents()
    print(f"  * Infrastructure Agents Count: {len(infra_agents)} (Roles: {[a.name for a in infra_agents[:3]]})")
    assert len(infra_agents) == 7
    print("  [OK] Infrastructure Division verified.\n")

    # Stage 10: Phase 8 Quality Division (5 Agents)
    print("Stage 10: Phase 8 Quality Division (5 Agents)")
    from app.ai.agents.divisions.quality import QualityDivision
    qa_agents = QualityDivision.get_agents()
    print(f"  * Quality Agents Count: {len(qa_agents)} (Roles: {[a.name for a in qa_agents[:3]]})")
    assert len(qa_agents) == 5
    print("  [OK] Quality Division verified.\n")

    # Stage 11: Phase 9 Security Division (5 Agents)
    print("Stage 11: Phase 9 Security Division (5 Agents)")
    from app.ai.agents.divisions.security import SecurityDivision
    sec_agents = SecurityDivision.get_agents()
    print(f"  * Security Agents Count: {len(sec_agents)} (Roles: {[a.name for a in sec_agents[:3]]})")
    assert len(sec_agents) == 5
    print("  [OK] Security Division verified.\n")

    # Stage 12: Inter-Agent Communication Bus & Event Broker
    print("Stage 12: Inter-Agent Communication Bus & Event Broker")
    from app.ai.agents.agent_bus import AgentMessageBus
    from app.ai.agents.models import AgentMessage
    bus = AgentMessageBus()
    await bus.publish_message(AgentMessage(sender_agent_id="ceo_agent", event_type="MISSION_DISPATCH"))
    listeners = bus.list_active_listeners()
    print(f"  * Bus Listeners ({len(listeners)}): {listeners[:4]}... | Published Message Count = {len(bus.get_message_history())}")
    assert len(listeners) == 9
    print("  [OK] Inter-Agent Communication Bus verified.\n")

    # Stage 13: Task Delegation Engine & Goal Decomposition DAG
    print("Stage 13: Task Delegation Engine & Goal Decomposition DAG")
    from app.ai.agents.delegation_engine import TaskDelegationEngine
    delegation = TaskDelegationEngine()
    dag = await delegation.decompose_goal("Build an Enterprise AI ERP Platform")
    print(f"  * Mission ID: '{dag.mission_id}' | Decomposed Task Nodes: {len(dag.task_nodes)}")
    for node in dag.task_nodes:
        print(f"    - [{node.assigned_division.value}] {node.title} -> {node.assigned_agent_id}")
    assert len(dag.task_nodes) >= 5
    print("  [OK] Task Delegation Engine verified.\n")

    # Stage 14: Parallel Execution & Task Dependency Resolution
    print("Stage 14: Parallel Execution & Task Dependency Resolution")
    exec_res = await delegation.execute_mission_dag(dag)
    print(f"  * Execution Outcome: Status = '{exec_res['status']}' | Progress = {exec_res['progress_percent']}%")
    assert exec_res["status"] == "COMPLETED"
    print("  [OK] Parallel Execution & Dependency Resolution verified.\n")

    # Stage 15: Multi-Agent Peer Review Quality Gates
    print("Stage 15: Multi-Agent Peer Review Quality Gates")
    from app.ai.agents.peer_review_engine import PeerReviewEngine
    from app.ai.agents.models import PeerReviewRequest
    review_engine = PeerReviewEngine()
    review_res = await review_engine.evaluate_deliverable(PeerReviewRequest(
        task_id="task_backend_01",
        author_agent_id="BackendEngineerAgent",
        content_to_review=exec_res,
    ))
    print(f"  * Peer Review ID: '{review_res.review_id}' | Approved = {review_res.approved} | Quality Score = {review_res.overall_quality_score}")
    print(f"  * Reviewer Signoffs: {list(review_res.reviewer_comments.keys())}")
    assert review_res.approved is True and review_res.overall_quality_score >= 0.85
    print("  [OK] Peer Review Quality Gates verified.\n")

    # Stage 16: Shared Agent Memory & Cross-Agent Context
    print("Stage 16: Shared Agent Memory & Cross-Agent Context")
    from app.ai.agents.shared_memory import SharedAgentMemory
    memory = SharedAgentMemory()
    memory.store("erp_architecture_blueprint", {"layers": 5, "database": "PostgreSQL"}, author="SoftwareArchitectAgent")
    retrieved = memory.retrieve("erp_architecture_blueprint")
    print(f"  * Retrieved Shared Memory: Layers = {retrieved['layers']} | DB = '{retrieved['database']}'")
    assert retrieved["database"] == "PostgreSQL"
    print("  [OK] Shared Agent Memory verified.\n")

    # Stage 17: Autonomous Agent Learning Engine
    print("Stage 17: Autonomous Agent Learning Engine")
    from app.ai.agents.agent_learning_engine import AgentLearningEngine
    learning = AgentLearningEngine()
    record = learning.record_learning("FAST_API_MICROSERVICE_WORKFLOW", ["Architect", "Implement", "SecurityAudit", "QA"])
    print(f"  * Recorded Learning Record: Pattern = '{record.pattern_name}' | Steps Count = {len(record.successful_steps)}")
    assert record.pattern_name == "FAST_API_MICROSERVICE_WORKFLOW"
    print("  [OK] Autonomous Agent Learning Engine verified.\n")

    # Stage 18: Voice-Driven Agent Workforce Orchestrator ("Nova, build ERP")
    print("Stage 18: Voice-Driven Agent Workforce Orchestrator ('Nova, build ERP')")
    voice_res = await engine.execute_voice_mission("Nova, build an Enterprise ERP platform")
    print(f"  * Voice Mission Response: Status = '{voice_res['status']}' | Peer Review Approved = {voice_res['peer_review_approved']}")
    print(f"  * Mission Quality Score = {voice_res['quality_score']} | Signoffs = {voice_res['reviewer_signoffs']}")
    assert voice_res["status"] == "DELIVERED" and voice_res["peer_review_approved"] is True
    print("  [OK] Voice-Driven Agent Workforce Orchestrator verified.\n")

    # Stage 19: Mission Dashboard Runtime & Organizational Telemetry
    print("Stage 19: Mission Dashboard Runtime & Organizational Telemetry")
    from app.ai.agents.dashboard_runtime import WorkforceDashboardRuntime
    dash_runtime = WorkforceDashboardRuntime()
    dash_snap = dash_runtime.get_dashboard_snapshot()
    print(f"  * Org Name: '{dash_snap['organization_name']}' | Divisions = {dash_snap['active_divisions_count']}")
    print(f"  * Total Agents = {dash_snap['total_agents_count']} | Approval Rate = {dash_snap['peer_review_approval_rate'] * 100}%")
    assert dash_snap["active_divisions_count"] == 9
    print("  [OK] Mission Dashboard Runtime verified.\n")

    # Stage 20: System Integration & Master Health Verification
    print("Stage 20: System Integration & Master Health Verification")
    master_health = engine.get_workforce_health()
    print(f"  * Master Workforce Health: Status = '{master_health.status}' | Registered Agents = {master_health.total_registered_agents}")
    assert master_health.is_healthy is True and master_health.total_registered_agents == 67
    print("  [OK] System Integration & Master Health Verification complete.\n")

    print("==================================================================")
    print("  ALL 20 STAGES PASSED SUCCESSFULLY!")
    print("  Universal Agent Workforce & Autonomous AI Company Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_20_stage_validation())
