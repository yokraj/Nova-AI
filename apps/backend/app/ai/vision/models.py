"""Domain models and schemas for the Enterprise Vision & Computer Interaction Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    """Normalized or absolute bounding box coordinates (x, y, width, height)."""
    x: float = Field(..., description="X coordinate of top-left corner.")
    y: float = Field(..., description="Y coordinate of top-left corner.")
    width: float = Field(..., description="Width of the bounding box.")
    height: float = Field(..., description="Height of the bounding box.")

class ScreenRegion(BaseModel):
    """Defines a targeted subset rectangular area on the screen."""
    x: int
    y: int
    width: int
    height: int

class UIElement(BaseModel):
    """A detected user interface control or component."""
    type: str = Field(..., description="Type of element (button, textbox, dropdown, etc.).")
    label: Optional[str] = Field(None, description="Extracted label or text of the control.")
    bbox: BoundingBox = Field(..., description="Bounding box of the element.")
    confidence: float = Field(1.0, description="Detection confidence score.")

class OCRBlock(BaseModel):
    """An individual block/word of text extracted by OCR."""
    text: str = Field(..., description="Extracted text string.")
    bbox: BoundingBox = Field(..., description="Bounding box containing this text block.")
    confidence: float = Field(1.0, description="OCR confidence score.")

class OCRResult(BaseModel):
    """The structured output of optical character recognition."""
    blocks: List[OCRBlock] = Field(default_factory=list, description="Detailed text blocks.")
    full_text: str = Field("", description="Consolidated plain text transcript.")
    confidence: float = Field(1.0, description="Average OCR confidence.")

class LayoutNode(BaseModel):
    """A hierarchical node representing screen UI containment structure."""
    name: str = Field(..., description="Node label or title.")
    type: str = Field(..., description="Node block type (e.g. Activity Bar, Explorer, Editor).")
    bbox: BoundingBox = Field(..., description="Bounding box bounds.")
    children: List["LayoutNode"] = Field(default_factory=list, description="Nested child nodes.")

class DetectedObject(BaseModel):
    """An object detected on the screen."""
    type: str = Field(..., description="Class name of the object.")
    confidence: float = Field(1.0, description="Detection confidence score.")
    bbox: BoundingBox = Field(..., description="Bounding box bounds.")

class ColorPalette(BaseModel):
    """Color analysis details of the screenshot."""
    dominant_colors: List[str] = Field(default_factory=list, description="Hex values of dominant colors.")
    theme: str = Field("dark", description="Calculated theme (light, dark).")
    brightness: float = Field(0.0, description="Calculated average brightness (0-255).")
    contrast: float = Field(0.0, description="Calculated average contrast.")

class ScreenshotMetadata(BaseModel):
    """Metadata for a captured screen image."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    width: int = Field(..., description="Image width in pixels.")
    height: int = Field(..., description="Image height in pixels.")
    format: str = Field("png", description="Image compression format.")

class ScreenAnalysis(BaseModel):
    """The results of screen visual processing."""
    elements: List[UIElement] = Field(default_factory=list)
    objects: List[DetectedObject] = Field(default_factory=list)
    layout_root: Optional[LayoutNode] = None

class ActionStep(BaseModel):
    """A single planned action for desktop interaction."""
    action_type: str = Field(..., description="Action name (click, type, wait, move).")
    target: Optional[str] = Field(None, description="Description of the target element.")
    location: Optional[BoundingBox] = Field(None, description="Bounding box target coordinates.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom arguments (e.g. text value, button type).")

class ActionPlan(BaseModel):
    """A compiled sequence of action steps to automate a visual task."""
    steps: List[ActionStep] = Field(default_factory=list, description="Ordered steps.")
    confidence: float = Field(1.0, description="Planning confidence score.")

class VisionMetrics(BaseModel):
    """Observability tracking metrics for vision pipeline execution."""
    load_time: float = Field(0.0, description="Duration in ms to load the image/source.")
    preprocessing_time: float = Field(0.0, description="Duration in ms to preprocess.")
    ocr_time: float = Field(0.0, description="Duration in ms for OCR processing.")
    detection_time: float = Field(0.0, description="Duration in ms for UI/object detection.")
    pipeline_time: float = Field(0.0, description="Total execution duration in ms.")

class VisionRequest(BaseModel):
    """Input request details for screenshot or image analysis."""
    image_path: Optional[str] = Field(None, description="Local path to image file.")
    image_bytes: Optional[bytes] = Field(None, description="Raw image bytes payload.")
    region: Optional[ScreenRegion] = Field(None, description="Target bounding region.")
    options: Dict[str, Any] = Field(default_factory=dict, description="Provider/Analysis custom flags.")

class VisionResponse(BaseModel):
    """Constituted payload output of the visual analysis pipeline."""
    status: str = Field("success", description="Outcome status (success, failed, partial).")
    metadata: ScreenshotMetadata = Field(..., description="Source capture details.")
    analysis: ScreenAnalysis = Field(..., description="Visual elements and objects discovered.")
    ocr: OCRResult = Field(..., description="Text extracted from image.")
    colors: ColorPalette = Field(..., description="Theme and color diagnostics.")
    action_plan: ActionPlan = Field(..., description="Planned action sequence steps.")
    metrics: VisionMetrics = Field(..., description="Execution performance statistics.")
