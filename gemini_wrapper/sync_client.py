"""Synchronous convenience wrapper around the async client."""

from __future__ import annotations

from typing import Any, Callable, Dict

import anyio

from .client import GeminiAsyncClient
from .config import EndpointPaths, Settings


class GeminiClient:
    """Blocking client that delegates work to ``GeminiAsyncClient``."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        paths: EndpointPaths | None = None,
        **overrides: Any,
    ) -> None:
        self._async_client = GeminiAsyncClient(settings, paths=paths, **overrides)
        self._closed = False

    @property
    def settings(self) -> Settings:
        return self._async_client.settings

    def complete(self, prompt: str, **opts: Any) -> Dict[str, Any]:
        return anyio.run(self._async_client.complete, prompt, **opts)

    def chat(self, messages: list[dict[str, Any]], **opts: Any) -> Dict[str, Any]:
        return anyio.run(self._async_client.chat, messages, **opts)

    def embed(self, texts: list[str], **opts: Any) -> Dict[str, Any]:
        return anyio.run(self._async_client.embed, texts, **opts)

    def stream_complete(self, prompt: str, callback: Callable[[str], None], **opts: Any) -> None:
        anyio.run(self._async_client.stream_complete, prompt, callback, **opts)

    def health_check(self) -> Dict[str, Any]:
        return anyio.run(self._async_client.health_check)

    def close(self) -> None:
        if self._closed:
            return
        try:
            anyio.run(self._async_client.aclose)
        except RuntimeError:
            # Event loop already closed, ignore
            pass
        self._closed = True

    def __enter__(self) -> "GeminiClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


__all__ = ["GeminiClient"]
