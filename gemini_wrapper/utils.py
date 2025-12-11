"""Shared helpers for gemini-wrapper."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable


def get_logger(logger: logging.Logger | None = None) -> logging.Logger:
    """Return a configured logger, attaching a default handler if needed."""
    if logger is not None:
        return logger

    logger = logging.getLogger("gemini_wrapper")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def redact_api_key(value: str | None) -> str:
    """Return a redacted representation of an API key for safe logging."""
    if not value:
        return "<missing>"
    if len(value) <= 4:
        return "****"
    return f"{value[:4]}...{value[-4:]}"


def build_headers(api_key: str, project: str | None = None, extra: Dict[str, str] | None = None) -> Dict[str, str]:
    """Construct default HTTP headers for API calls."""
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if project:
        headers["X-Project"] = project
    if extra:
        headers.update(extra)
    return headers


def flatten_stream_chunks(chunks: Iterable[str]) -> str:
    """Concatenate string chunks from a streaming response."""
    return "".join(chunks)


__all__ = ["get_logger", "redact_api_key", "build_headers", "flatten_stream_chunks"]
