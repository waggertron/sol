"""Shared UTC timestamp normalization for Style Kit domain services."""

from __future__ import annotations

from datetime import datetime, timezone


def normalize_utc_iso(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp with timezone") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalized_utc_datetime(value: str) -> datetime:
    """Parse a value already emitted by normalize_utc_iso for ordering checks."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
