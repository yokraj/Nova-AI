"""Configuration layer for the Enterprise Vision & Computer Interaction Engine.
"""

from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field

class OCRConfiguration(BaseModel):
    """Configuration options for OCR engines."""
    enabled: bool = Field(True, description="Enables/disables text extraction.")
    languages: str = Field("eng", description="Tesseract language tags.")
    engine: str = Field("pytesseract", description="Target OCR engine (pytesseract, easyocr, mock).")
    confidence_threshold: float = Field(0.5, description="Min text match score.")

class ScreenshotConfiguration(BaseModel):
    """Configuration options for screen capturing drivers."""
    backend: str = Field("native", description="Screenshot backend (native, pillow, mock).")
    save_raw: bool = Field(False, description="Persist screenshots physically.")
    raw_dir: str = Field(".nova/screenshots", description="Storage dir for raw captures.")

class CVConfiguration(BaseModel):
    """Configuration options for local computer vision engines."""
    enabled: bool = Field(True, description="Enables/disables OpenCV/Pillow logic.")
    max_image_size: Tuple[int, int] = Field((1920, 1080), description="Max scaling bounds.")
    resize_policy: str = Field("scale_down", description="Scaling behavior if oversized.")
    preprocessing_options: Dict[str, Any] = Field(default_factory=dict, description="Image pre-processing parameters.")

class VisionConfiguration(BaseModel):
    """Aggregated Vision Engine configuration parameters."""
    enabled: bool = Field(True, description="Enables vision services.")
    provider: str = Field("local_cv", description="Default provider (local_cv, ollama_vision, mock).")
    confidence_threshold: float = Field(0.5, description="General confidence filter score.")
    image_cache_enabled: bool = Field(True, description="Cache results of analyzed screens.")
    offline_mode: bool = Field(True, description="Enforce local-only execution.")
    gpu_detection: bool = Field(False, description="Enables GPU model acceleration.")
    debug_mode: bool = Field(False, description="Enables verbose debugging overlays.")
    
    ocr: OCRConfiguration = Field(default_factory=OCRConfiguration)
    screenshot: ScreenshotConfiguration = Field(default_factory=ScreenshotConfiguration)
    cv: CVConfiguration = Field(default_factory=CVConfiguration)
