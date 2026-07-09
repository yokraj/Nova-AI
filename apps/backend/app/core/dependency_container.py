"""Dependency injection container mapping for Nova AI.

Implements provider registries, singleton caching, factory builders,
and FastAPI helper resolution adapters for core repositories and services.
"""

from typing import Any, Callable, Dict, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.database.unit_of_work import UnitOfWork
from app.identity.infrastructure.token_repository import RefreshTokenRepository
from app.identity.infrastructure.user_repository import UserRepository
from app.identity.services.auth_service import AuthService
from app.identity.services.user_service import UserService

logger = structlog.get_logger(__name__)
T = TypeVar("T")


class Provider:
    """Base abstract provider interface."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Resolves the dependency value.

        Raises:
            NotImplementedError: If not overridden by subclass.
        """
        raise NotImplementedError


class SingletonProvider(Provider):
    """Caches and returns a single resolved instance of a dependency."""

    def __init__(
        self, factory: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        self._factory = factory
        self._args = args
        self._kwargs = kwargs
        self._instance: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._instance is None:
            logger.debug(
                "resolving_singleton_dependency",
                factory=self._factory.__name__
                if hasattr(self._factory, "__name__")
                else str(self._factory),
            )
            self._instance = self._factory(*self._args, **self._kwargs)
        return self._instance


class FactoryProvider(Provider):
    """Instantiates a fresh instance of a dependency on every call."""

    def __init__(
        self, factory: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        self._factory = factory
        self._args = args
        self._kwargs = kwargs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        logger.debug(
            "resolving_factory_dependency",
            factory=self._factory.__name__
            if hasattr(self._factory, "__name__")
            else str(self._factory),
        )
        return self._factory(*self._args, **self._kwargs)


class DependencyContainer:
    """Central container registering interfaces and resolving dependencies."""

    def __init__(self) -> None:
        self._providers: Dict[Type[Any], Provider] = {}

    def register(self, interface: Type[T], provider: Provider) -> None:
        """Registers a provider for a target interface or class type.

        Args:
            interface: The interface or implementation class key to map.
            provider: The provider instance producing the target dependency.
        """
        self._providers[interface] = provider

    def resolve(self, interface: Type[T]) -> T:
        """Resolves and returns a registered dependency for an interface.

        Args:
            interface: The interface or implementation class key to resolve.

        Returns:
            The resolved dependency instance.
        """
        provider = self._providers.get(interface)
        if not provider:
            logger.error(
                "dependency_resolution_failed",
                interface=interface.__name__
                if hasattr(interface, "__name__")
                else str(interface),
            )
            raise ValueError(
                f"No provider registered for interface: {interface}"
            )
        return provider()

    def clear(self) -> None:
        """Clears all registered providers and caches."""
        self._providers.clear()


# Global dependency container instance
container = DependencyContainer()


def resolve(interface: Type[T]) -> T:
    """Utility hook resolving dependencies directly from the global container.

    Args:
        interface: The interface or class to resolve.

    Returns:
        The resolved dependency instance.
    """
    return container.resolve(interface)


# ==========================================================
# Core Infrastructure Dependency Providers
# ==========================================================


def register_request_dependencies(session: AsyncSession) -> None:
    """Registers database repositories and business services bound to request session.

    Args:
        session: Active request SQLAlchemy AsyncSession.
    """
    # 1. Register UnitOfWork
    uow = UnitOfWork()
    # Bind UoW session directly for inline repository consistency
    uow.session = session
    container.register(UnitOfWork, SingletonProvider(lambda: uow))

    # 2. Register Repositories
    from app.identity.infrastructure.session_repository import SessionRepository
    from app.identity.repositories.interfaces import (
        IUserRepository,
        ISessionRepository,
        IRefreshTokenRepository,
    )

    user_repo = UserRepository(session)
    token_repo = RefreshTokenRepository(session)
    session_repo = SessionRepository(session)

    container.register(UserRepository, SingletonProvider(lambda: user_repo))
    container.register(
        RefreshTokenRepository, SingletonProvider(lambda: token_repo)
    )
    container.register(
        SessionRepository, SingletonProvider(lambda: session_repo)
    )

    container.register(IUserRepository, SingletonProvider(lambda: user_repo))
    container.register(
        IRefreshTokenRepository, SingletonProvider(lambda: token_repo)
    )
    container.register(
        ISessionRepository, SingletonProvider(lambda: session_repo)
    )

    # 3. Register Services
    user_service = UserService(user_repo)
    auth_service = AuthService(uow, user_repo, token_repo)
    container.register(UserService, SingletonProvider(lambda: user_service))
    container.register(AuthService, SingletonProvider(lambda: auth_service))


def register_ai_gateway_dependencies() -> None:
    """Registers singleton providers for the AI Gateway registries, costs estimators, and service."""
    from app.ai.cost import CostEstimator
    from app.ai.gateway import AiGatewayService
    from app.ai.health import HealthMonitor
    from app.ai.registry import ModelRegistry, ProviderRegistry
    from app.core.config import settings

    provider_registry = ProviderRegistry()
    model_registry = ModelRegistry()
    cost_estimator = CostEstimator(model_registry)
    health_monitor = HealthMonitor()
    ai_gateway = AiGatewayService(
        provider_registry=provider_registry,
        model_registry=model_registry,
        cost_estimator=cost_estimator,
        health_monitor=health_monitor,
        default_model=settings.AI_DEFAULT_MODEL,
        max_retries=settings.AI_MAX_RETRIES,
        timeout_seconds=settings.AI_TIMEOUT_SECONDS,
    )

    container.register(
        ProviderRegistry, SingletonProvider(lambda: provider_registry)
    )
    container.register(
        ModelRegistry, SingletonProvider(lambda: model_registry)
    )
    container.register(
        CostEstimator, SingletonProvider(lambda: cost_estimator)
    )
    container.register(
        HealthMonitor, SingletonProvider(lambda: health_monitor)
    )
    container.register(
        AiGatewayService, SingletonProvider(lambda: ai_gateway)
    )


def register_workflow_dependencies() -> None:
    """Registers singleton providers for Workflow event bus, execution engine, and service."""
    from app.automation.engine import WorkflowExecutionEngine
    from app.automation.event_bus import EventBus
    from app.automation.services import WorkflowService

    event_bus = EventBus()
    execution_engine = WorkflowExecutionEngine(event_bus)
    workflow_service = WorkflowService(execution_engine)

    container.register(EventBus, SingletonProvider(lambda: event_bus))
    container.register(
        WorkflowExecutionEngine, SingletonProvider(lambda: execution_engine)
    )
    container.register(
        WorkflowService, SingletonProvider(lambda: workflow_service)
    )


def register_runtime_dependencies() -> None:
    """Registers singleton providers for the Runtime Kernel and Runtime Manager."""
    from app.runtime.kernel import RuntimeKernel
    from app.runtime.runtime_manager import RuntimeManager

    kernel = RuntimeKernel()
    runtime_manager = RuntimeManager(kernel)

    container.register(RuntimeKernel, SingletonProvider(lambda: kernel))
    container.register(RuntimeManager, SingletonProvider(lambda: runtime_manager))



