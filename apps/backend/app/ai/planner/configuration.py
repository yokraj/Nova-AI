"""Configuration models for the Intelligent Planner & Task Decomposition Engine.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class PlannerConfiguration(BaseSettings):
    """Configuration settings for the main planner engine."""
    model_config = SettingsConfigDict(env_prefix="NOVA_PLANNER_")
    
    enabled: bool = True
    planning_timeout: float = 300.0
    planner_model: str = "llama3"
    confidence_threshold: float = 0.7
    cost_estimation_mode: str = "token_based"  # token_based, compute_based

class GoalConfiguration(BaseSettings):
    """Configuration settings for goal analyzer."""
    model_config = SettingsConfigDict(env_prefix="NOVA_PLANNER_GOAL_")
    
    recursion_depth: int = 5
    default_complexity_threshold: float = 0.5

class DAGConfiguration(BaseSettings):
    """Configuration settings for dependency graph building."""
    model_config = SettingsConfigDict(env_prefix="NOVA_PLANNER_DAG_")
    
    cycle_detection_enabled: bool = True
    strict_dependencies: bool = True

class SchedulerConfiguration(BaseSettings):
    """Configuration settings for execution batches scheduler."""
    model_config = SettingsConfigDict(env_prefix="NOVA_PLANNER_SCHEDULER_")
    
    scheduling_strategy: str = "topological_batch"  # topological_batch, critical_path_first
    parallel_task_limits: int = 4

class OptimizationConfiguration(BaseSettings):
    """Configuration settings for graph optimization."""
    model_config = SettingsConfigDict(env_prefix="NOVA_PLANNER_OPTIMIZER_")
    
    optimization_enabled: bool = True
    optimization_level: int = 2  # 1: basic, 2: full merges

class RecoveryConfiguration(BaseSettings):
    """Configuration settings for recovery planner."""
    model_config = SettingsConfigDict(env_prefix="NOVA_PLANNER_RECOVERY_")
    
    retry_count: int = 3
    enable_degraded_mode: bool = True

class MultiAgentPlannerConfiguration(BaseSettings):
    """Consolidated planning subsystem settings."""
    model_config = SettingsConfigDict(env_prefix="NOVA_PLANNER_MAIN_")
    
    planner: PlannerConfiguration = Field(default_factory=PlannerConfiguration)
    goal: GoalConfiguration = Field(default_factory=GoalConfiguration)
    dag: DAGConfiguration = Field(default_factory=DAGConfiguration)
    scheduler: SchedulerConfiguration = Field(default_factory=SchedulerConfiguration)
    optimizer: OptimizationConfiguration = Field(default_factory=OptimizationConfiguration)
    recovery: RecoveryConfiguration = Field(default_factory=RecoveryConfiguration)
