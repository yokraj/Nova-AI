"""Trend Analyzer Module.

Computes moving/rolling averages, growth rates, linear trend directions
(Increasing, Stable, Decreasing), and short-term linear extrapolation forecasts.
"""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(__name__)


class TrendAnalyzer:
    """Calculates trend directional vectors, moving averages, and growth rates."""

    def __init__(self) -> None:
        logger.info("trend_analyzer_initialized")

    def moving_average(self, values: List[float], window: int = 3) -> List[float]:
        """Calculates simple moving average over sliding window size."""
        if not values or window <= 0:
            return []
        result = []
        for i in range(len(values)):
            start_idx = max(0, i - window + 1)
            sub_vals = values[start_idx : i + 1]
            result.append(round(sum(sub_vals) / len(sub_vals), 2))
        return result

    def rolling_average(self, values: List[float], window: int = 5) -> List[float]:
        """Alias for moving_average."""
        return self.moving_average(values, window)

    def growth_rate(self, values: List[float]) -> float:
        """Calculates percentage growth rate from initial to final value."""
        if len(values) < 2 or values[0] == 0:
            return 0.0
        initial = values[0]
        final = values[-1]
        rate = ((final - initial) / abs(initial)) * 100.0
        return round(rate, 2)

    def calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Classifies directional vector (Increasing, Stable, Decreasing) and slope."""
        if len(values) < 2:
            return {"direction": "Stable", "slope": 0.0, "growth_rate": 0.0}

        growth = self.growth_rate(values)
        if growth > 5.0:
            direction = "Increasing"
        elif growth < -5.0:
            direction = "Decreasing"
        else:
            direction = "Stable"

        slope = (values[-1] - values[0]) / (len(values) - 1)

        return {
            "direction": direction,
            "slope": round(slope, 4),
            "growth_rate_percent": growth,
            "sample_count": len(values),
        }

    def forecast_placeholder(self, values: List[float], steps: int = 3) -> List[float]:
        """Performs simple linear extrapolation forecast for future steps."""
        if not values:
            return [0.0] * steps
        if len(values) == 1:
            return [values[0]] * steps

        slope = (values[-1] - values[0]) / (len(values) - 1)
        last_val = values[-1]

        forecast = []
        for i in range(1, steps + 1):
            projected = last_val + (slope * i)
            forecast.append(round(max(0.0, projected), 2))
        return forecast
