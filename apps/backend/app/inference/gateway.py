"""Inference Gateway Master Module.

Central entry point and routing gateway for every AI request across Nova Operating System.
"""

from typing import Any, Dict, List, Optional
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.inference.config import InferenceConfig
from app.inference.repository import InferenceRepository
from app.inference.service import (
    InferenceService,
    GatewayService,
    ModelService,
    StreamingService,
    BenchmarkService,
)

logger = structlog.get_logger(__name__)


class InferenceGateway:
    """Enterprise Master Inference Gateway Execution Layer."""

    def __init__(
        self, session: Optional[AsyncSession] = None, config: Optional[InferenceConfig] = None
    ) -> None:
        self.session = session
        self.config = config or InferenceConfig()
        self.repository = InferenceRepository(session=session)

        # Service Abstractions Initialization
        self.inference_service = InferenceService(repository=self.repository)
        self.gateway_service = GatewayService(repository=self.repository)
        self.model_service = ModelService(repository=self.repository)
        self.streaming_service = StreamingService(repository=self.repository)
        self.benchmark_service = BenchmarkService(repository=self.repository)

        logger.info("inference_gateway_master_initialized")
