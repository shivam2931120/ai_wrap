"""Configuration utilities for gemini-wrapper."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping, MutableMapping, Optional

from dotenv import load_dotenv


def _load_env_once() -> None:
    """Load environment variables from a .env file once."""
    # load_dotenv caches internally, so repeated calls are cheap.
    load_dotenv(override=False)


@dataclass
class EndpointPaths:
    """Provider-specific relative paths for each operation."""

    complete: str = "/v1beta/models/gemini-2.5-flash:generateContent"
    chat: str = "/v1beta/models/gemini-2.5-flash:generateContent"
    embed: str = "/v1beta/models/text-embedding-004:embedContent"
    stream_complete: str = "/v1beta/models/gemini-2.5-flash:streamGenerateContent"
    health: str = "/v1beta/models/gemini-2.5-flash:generateContent"


@dataclass
class Settings:
    """Runtime settings derived from environment variables."""

    api_key: str
    endpoint: str
    timeout: float = 30.0
    max_retries: int = 3
    project: Optional[str] = None
    paths: EndpointPaths = field(default_factory=EndpointPaths)

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | MutableMapping[str, str] | None = None,
        *,
        paths: EndpointPaths | None = None,
    ) -> "Settings":
        """Create settings using environment variables (with optional overrides)."""

        _load_env_once()
        source = env if env is not None else os.environ

        api_key = source.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set")

        endpoint = source.get("GEMINI_API_ENDPOINT")
        if not endpoint:
            raise ValueError("GEMINI_API_ENDPOINT must be set")

        timeout_value = source.get("GEMINI_TIMEOUT")
        timeout = float(timeout_value) if timeout_value else 30.0

        max_retries_value = source.get("GEMINI_MAX_RETRIES")
        max_retries = int(max_retries_value) if max_retries_value else 3
        if max_retries < 0:
            raise ValueError("GEMINI_MAX_RETRIES must be non-negative")

        project = source.get("GEMINI_PROJECT")

        return cls(
            api_key=api_key,
            endpoint=endpoint,
            timeout=timeout,
            max_retries=max_retries,
            project=project,
            paths=paths if paths is not None else EndpointPaths(),
        )


__all__ = ["EndpointPaths", "Settings"]
