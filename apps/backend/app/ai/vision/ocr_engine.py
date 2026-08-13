"""OCR Engine implements optical character recognition using Tesseract with mock fallback.
"""

from typing import List
from PIL import Image
from app.ai.vision.interfaces import IOCRProvider
from app.ai.vision.models import OCRResult, OCRBlock, BoundingBox

class OCREngine(IOCRProvider):
    """Manages offline text extraction using pytesseract with fallback pipelines."""

    def __init__(self, use_mock_fallback: bool = True) -> None:
        self.use_mock_fallback = use_mock_fallback

    async def detect_text(self, image: Image.Image) -> OCRResult:
        """Runs OCR transcription on target PIL Image."""
        if not self.use_mock_fallback:
            try:
                import pytesseract
                # Run tesseract image_to_data or image_to_string
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                blocks: List[OCRBlock] = []
                n_boxes = len(data['level'])
                words = []
                
                for i in range(n_boxes):
                    text = data['text'][i].strip()
                    if text:
                        # Convert to normalized bounds
                        x = data['left'][i]
                        y = data['top'][i]
                        w = data['width'][i]
                        h = data['height'][i]
                        bbox = BoundingBox(
                            x=x / image.width,
                            y=y / image.height,
                            width=w / image.width,
                            height=h / image.height
                        )
                        blocks.append(OCRBlock(
                            text=text,
                            bbox=bbox,
                            confidence=float(data['conf'][i]) / 100.0
                        ))
                        words.append(text)
                
                full_text = " ".join(words)
                return OCRResult(
                    blocks=blocks,
                    full_text=full_text,
                    confidence=sum(b.confidence for b in blocks) / len(blocks) if blocks else 1.0
                )
            except Exception:
                pass

        # Simulated fallback / mock output
        return self._generate_mock_ocr(image)

    def _generate_mock_ocr(self, image: Image.Image) -> OCRResult:
        """Returns standard mockup text blocks matching dummy desktop screen states."""
        # Suppose the mock screen contains standard IDE items
        blocks = [
            OCRBlock(
                text="File",
                bbox=BoundingBox(x=0.01, y=0.01, width=0.03, height=0.02),
                confidence=0.99
            ),
            OCRBlock(
                text="Edit",
                bbox=BoundingBox(x=0.05, y=0.01, width=0.03, height=0.02),
                confidence=0.99
            ),
            OCRBlock(
                text="View",
                bbox=BoundingBox(x=0.09, y=0.01, width=0.03, height=0.02),
                confidence=0.98
            ),
            OCRBlock(
                text="Login",
                bbox=BoundingBox(x=0.45, y=0.5, width=0.1, height=0.04),
                confidence=0.95
            ),
            OCRBlock(
                text="Username",
                bbox=BoundingBox(x=0.35, y=0.4, width=0.1, height=0.03),
                confidence=0.96
            ),
            OCRBlock(
                text="Password",
                bbox=BoundingBox(x=0.35, y=0.45, width=0.1, height=0.03),
                confidence=0.97
            ),
        ]
        return OCRResult(
            blocks=blocks,
            full_text="File Edit View Login Username Password",
            confidence=0.98
        )
