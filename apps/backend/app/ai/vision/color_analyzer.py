"""Color Analyzer details theme colors and contrast.
"""

from PIL import Image, ImageStat
from app.ai.vision.models import ColorPalette

class ColorAnalyzer:
    """Analyzes pixels to classify light/dark modes and average brightness."""

    def analyze_colors(self, image: Image.Image) -> ColorPalette:
        """Determines contrast, brightness, and calculates dominant color codes."""
        # Calculate average brightness using ImageStat
        stat = ImageStat.Stat(image.convert("L"))
        brightness = stat.mean[0]

        # Calculate contrast using standard deviation of grayscale channel
        contrast = stat.stddev[0]

        theme = "dark" if brightness < 127 else "light"

        # Determine dominant colors (sample simple color palette)
        # Resize to 8x8 pixels to get primary color patches
        resized = image.resize((8, 8))
        colors = resized.getcolors(64)
        
        dominant = []
        if colors:
            # Sort by frequency descending
            sorted_colors = sorted(colors, key=lambda c: c[0], reverse=True)
            for count, rgb in sorted_colors[:5]:
                # Format to hex string
                if isinstance(rgb, tuple) and len(rgb) >= 3:
                    hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                    dominant.append(hex_color)

        # Fallback if empty
        if not dominant:
            dominant = ["#1e1e1e", "#ffffff", "#007acc"]

        return ColorPalette(
            dominant_colors=dominant,
            theme=theme,
            brightness=brightness,
            contrast=contrast
        )
