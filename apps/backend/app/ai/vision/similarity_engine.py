"""Similarity Engine compares layout similarity for visual regression checks.
"""

from PIL import Image, ImageChops, ImageStat
from app.ai.vision.interfaces import ISimilarityEngine

class SimilarityEngine(ISimilarityEngine):
    """Compares image differences using pixel-wise standard deviations."""

    def calculate_similarity(self, image_a: Image.Image, image_b: Image.Image) -> float:
        """Determines similarity coefficient from 0.0 (different) to 1.0 (identical)."""
        # Ensure dimensions match
        if image_a.size != image_b.size:
            # Resize image B to match image A
            image_b = image_b.resize(image_a.size)

        # 1. Pixel difference calculation
        diff = ImageChops.difference(image_a, image_b)
        stat = ImageStat.Stat(diff.convert("L"))
        
        # Mean difference (0 means identical, 255 completely different)
        mean_diff = stat.mean[0]
        similarity = 1.0 - (mean_diff / 255.0)

        # 2. Add histogram similarity if available via OpenCV
        try:
            import cv2
            import numpy as np
            # Convert PIL to CV images
            cv_a = cv2.cvtColor(np.array(image_a), cv2.COLOR_RGB2BGR)
            cv_b = cv2.cvtColor(np.array(image_b), cv2.COLOR_RGB2BGR)
            
            hist_a = cv2.calcHist([cv_a], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist_b = cv2.calcHist([cv_b], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            
            cv2.normalize(hist_a, hist_a)
            cv2.normalize(hist_b, hist_b)
            
            hist_sim = cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_CORREL)
            # Correlation goes from -1 to 1. Normalize to 0-1
            hist_sim = max(0.0, (hist_sim + 1.0) / 2.0)
            
            # Combine both metrics
            similarity = (similarity * 0.4) + (hist_sim * 0.6)
        except Exception:
            pass

        return float(round(similarity, 4))
