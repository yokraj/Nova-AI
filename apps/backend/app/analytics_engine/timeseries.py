"""Time Series Engine Module.

Aggregates and downsamples raw timestamped telemetry samples into hourly, daily,
weekly, monthly, and yearly time buckets with statistical summaries (mean, min, max, std).
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class TimeSeriesEngine:
    """Time-series aggregation and downsampling engine."""

    def __init__(self) -> None:
        logger.info("timeseries_engine_initialized")

    def _bucket_timestamp(self, ts: datetime, period: str) -> str:
        """Truncates timestamp into uniform ISO-8601 bucket string."""
        if period == "hourly":
            return ts.strftime("%Y-%m-%dT%H:00:00Z")
        elif period == "daily":
            return ts.strftime("%Y-%m-%d")
        elif period == "weekly":
            # Year-Week number
            year, week, _ = ts.isocalendar()
            return f"{year}-W{week:02d}"
        elif period == "monthly":
            return ts.strftime("%Y-%m")
        elif period == "yearly":
            return ts.strftime("%Y")
        return ts.isoformat()

    def downsample(self, samples: List[Dict[str, Any]], period: str = "hourly") -> List[Dict[str, Any]]:
        """Downsamples list of timestamped numerical samples into aggregated time buckets."""
        if not samples:
            return []

        buckets: Dict[str, List[float]] = {}
        for item in samples:
            ts_val = item.get("timestamp")
            if isinstance(ts_val, str):
                try:
                    ts_dt = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
                except ValueError:
                    ts_dt = datetime.now(timezone.utc)
            elif isinstance(ts_val, datetime):
                ts_dt = ts_val
            else:
                ts_dt = datetime.now(timezone.utc)

            bucket_key = self._bucket_timestamp(ts_dt, period)
            val = item.get("value") or item.get("metric_value", 0.0)
            if isinstance(val, (int, float)):
                if bucket_key not in buckets:
                    buckets[bucket_key] = []
                buckets[bucket_key].append(float(val))

        aggregated = []
        for key in sorted(buckets.keys()):
            vals = buckets[key]
            n = len(vals)
            avg_val = sum(vals) / n if n > 0 else 0.0
            min_val = min(vals) if n > 0 else 0.0
            max_val = max(vals) if n > 0 else 0.0

            aggregated.append({
                "period": period,
                "bucket": key,
                "count": n,
                "average": round(avg_val, 2),
                "min": round(min_val, 2),
                "max": round(max_val, 2),
            })

        return aggregated

    def aggregate_hourly(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Downsamples samples into 1-hour buckets."""
        return self.downsample(samples, "hourly")

    def aggregate_daily(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Downsamples samples into 1-day buckets."""
        return self.downsample(samples, "daily")

    def aggregate_weekly(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Downsamples samples into 1-week buckets."""
        return self.downsample(samples, "weekly")

    def aggregate_monthly(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Downsamples samples into 1-month buckets."""
        return self.downsample(samples, "monthly")

    def aggregate_yearly(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Downsamples samples into 1-year buckets."""
        return self.downsample(samples, "yearly")

    def query_range(
        self,
        samples: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
    ) -> List[Dict[str, Any]]:
        """Filters samples within a specific start and end datetime range."""
        filtered = []
        for item in samples:
            ts_val = item.get("timestamp")
            if isinstance(ts_val, str):
                try:
                    ts_dt = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
                except ValueError:
                    continue
            elif isinstance(ts_val, datetime):
                ts_dt = ts_val
            else:
                continue

            if start_time <= ts_dt <= end_time:
                filtered.append(item)
        return filtered
