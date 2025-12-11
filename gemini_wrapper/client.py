# client.py
"""Async HTTP client for Gemini-style APIs with retry/backoff support.

This module provides `GeminiAsyncClient` along with small helpers required
for robust retries and logging. It expects `Settings` and `EndpointPaths`
to be available from `gemini_wrapper.config`.
"""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import replace
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx

from .config import Settings, EndpointPaths

# Retryable HTTP status codes
_RETRY_STATUS = {429, 502, 503, 504}

# Backoff defaults
_DEFAULT_BACKOFF_BASE = 1.0
_MAX_BACKOFF_SECONDS = 60.0


def get_logger(logger: Optional[logging.Logger] = None) -> logging.Logger:
    return logger or logging.getLogger("gemini_wrapper")


def redact_api_key(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


def build_headers(api_key: Optional[str], project: Optional[str], extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if project:
        headers["X-Goog-Project-Id"] = project
    if extra:
        headers.update(extra)
    return headers


# ----- GeminiAsyncClient -----

class GeminiAsyncClient:
    """High-level async client for Gemini-compatible HTTP APIs."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        logger: logging.Logger | None = None,
        async_client: httpx.AsyncClient | None = None,
        paths: EndpointPaths | None = None,
        api_key: str | None = None,
        endpoint: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        project: str | None = None,
        # New optional overrides for interactive usage:
        max_retries_override: int | None = None,
        backoff_base: float | None = None,
        max_backoff_seconds: float | None = None,
    ) -> None:
        # obtain or build settings
        if settings is None:
            settings = Settings.from_env(paths=paths)
        elif paths is not None:
            settings = replace(settings, paths=paths)

        # apply direct overrides if provided
        if api_key is not None:
            settings.api_key = api_key
        if endpoint is not None:
            settings.endpoint = endpoint
        if timeout is not None:
            settings.timeout = timeout
        if max_retries is not None:
            settings.max_retries = max_retries
        if project is not None:
            settings.project = project

        # provide safe defaults if Settings implementation doesn't set them
        # (avoid attribute errors during initialization)
        if not hasattr(settings, "endpoint") or not settings.endpoint:
            settings.endpoint = getattr(settings, "endpoint", "https://generativelanguage.googleapis.com")
        if not hasattr(settings, "timeout") or settings.timeout is None:
            settings.timeout = getattr(settings, "timeout", 30.0)
        # allow Settings to not have max_retries; default to 3
        base_max_retries = getattr(settings, "max_retries", None)
        if base_max_retries is None:
            base_max_retries = 3
            settings.max_retries = base_max_retries

        self._settings = settings
        self._logger = get_logger(logger)
        self._client = async_client or httpx.AsyncClient(timeout=self._settings.timeout)
        self._owns_client = async_client is None

        # instance-level retry/backoff configuration (defaults to settings or module constants)
        self._max_retries = max_retries_override if max_retries_override is not None else int(self._settings.max_retries)
        self._backoff_base = backoff_base if backoff_base is not None else _DEFAULT_BACKOFF_BASE
        self._max_backoff_seconds = max_backoff_seconds if max_backoff_seconds is not None else _MAX_BACKOFF_SECONDS

        # safe minimums
        if not isinstance(self._max_retries, int) or self._max_retries < 0:
            self._max_retries = 0
        if not isinstance(self._backoff_base, (int, float)) or self._backoff_base <= 0:
            self._backoff_base = _DEFAULT_BACKOFF_BASE
        if not isinstance(self._max_backoff_seconds, (int, float)) or self._max_backoff_seconds <= 0:
            self._max_backoff_seconds = _MAX_BACKOFF_SECONDS

    @property
    def settings(self) -> Settings:
        """Expose the immutable settings."""
        return self._settings

    async def __aenter__(self) -> "GeminiAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore[override]
        await self.aclose()

    async def aclose(self) -> None:
        """Close the internal HTTP client if owned."""
        if self._owns_client:
            await self._client.aclose()

    def _build_url(self, path: str) -> str:
        base = str(self._settings.endpoint).rstrip("/")
        path = path if path.startswith("/") else f"/{path}"
        url = f"{base}{path}"
        # Add API key as query parameter for Google Gemini if present
        if getattr(self._settings, "api_key", None):
            return f"{url}?key={self._settings.api_key}"
        return url

    def _headers(self, extra: Dict[str, str] | None = None) -> Dict[str, str]:
        return build_headers(getattr(self._settings, "api_key", None), getattr(self._settings, "project", None), extra=extra)

    async def complete(self, prompt: str, **opts: Any) -> Dict[str, Any]:
        # Format for Google Gemini API
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        payload.update(opts)
        response = await self._request("POST", getattr(self._settings.paths, "complete"), json=payload)
        return response

    async def chat(self, messages: list[dict[str, Any]], **opts: Any) -> Dict[str, Any]:
        # Convert to Gemini format
        contents = [{"parts": [{"text": msg.get("content", "")}], "role": msg.get("role", "user")} for msg in messages]
        payload: Dict[str, Any] = {"contents": contents}
        payload.update(opts)
        response = await self._request("POST", getattr(self._settings.paths, "chat"), json=payload)
        return response

    async def embed(self, texts: list[str], **opts: Any) -> Dict[str, Any]:
        # Gemini embedding format
        if len(texts) == 1:
            content = {"parts": [{"text": texts[0]}]}
        else:
            content = {"parts": [{"text": t} for t in texts]}
        payload: Dict[str, Any] = {"content": content} if len(texts) == 1 else content
        payload.update(opts)
        response = await self._request("POST", getattr(self._settings.paths, "embed"), json=payload)
        return response

    async def stream_complete(self, prompt: str, callback: Callable[[str], None], **opts: Any) -> None:
        # Gemini streaming format
        payload: Dict[str, Any] = {"contents": [{"parts": [{"text": prompt}]}]}
        payload.update(opts)
        path = getattr(self._settings.paths, "stream_complete", None) or getattr(self._settings.paths, "complete")
        await self._stream_request("POST", path, payload, callback)

    async def health_check(self) -> Dict[str, Any]:
        response = await self._request("GET", getattr(self._settings.paths, "health"))
        return response

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Dict[str, Any] | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> Dict[str, Any]:
        attempt = 0
        url = self._build_url(path)
        while True:
            start = asyncio.get_event_loop().time()
            try:
                response = await self._client.request(
                    method,
                    url,
                    headers=self._headers(),
                    json=json,
                    timeout=timeout or self._settings.timeout,
                )
            except httpx.RequestError as exc:  # Network issues, timeouts, etc.
                elapsed = asyncio.get_event_loop().time() - start
                self._logger.debug("request error (elapsed=%.2fs): %s", elapsed, repr(exc))
                if not self._should_retry_exception(attempt):
                    raise
                delay = self._compute_delay(attempt, None)
                self._log_retry(attempt, delay, error=repr(exc))
                await asyncio.sleep(delay)
                attempt += 1
                continue

            elapsed = asyncio.get_event_loop().time() - start
            self._logger.debug("response received (status=%s, elapsed=%.2fs)", response.status_code, elapsed)

            if self._should_retry_response(response, attempt):
                delay = self._compute_delay(attempt, response)
                self._log_retry(
                    attempt,
                    delay,
                    status=response.status_code,
                    retry_after=(response.headers.get("Retry-After") if response.headers is not None else None),
                )
                await asyncio.sleep(delay)
                attempt += 1
                continue

            response.raise_for_status()
            if not response.content:
                return {}
            try:
                return response.json()
            except ValueError:
                return {"raw": response.text}

    async def _stream_request(
        self,
        method: str,
        path: str,
        payload: Dict[str, Any],
        callback: Callable[[str], None],
    ) -> None:
        attempt = 0
        url = self._build_url(path)
        timeout: float | httpx.Timeout | None = self._settings.timeout
        while True:
            start = asyncio.get_event_loop().time()
            try:
                async with self._client.stream(
                    method,
                    url,
                    headers=self._headers(),
                    json=payload,
                    timeout=timeout,
                ) as response:
                    if self._should_retry_response(response, attempt):
                        # drain the body before retrying
                        try:
                            await response.aread()
                        except Exception:
                            pass
                        delay = self._compute_delay(attempt, response)
                        self._log_retry(
                            attempt,
                            delay,
                            status=response.status_code,
                            retry_after=(response.headers.get("Retry-After") if response.headers is not None else None),
                        )
                        await asyncio.sleep(delay)
                        attempt += 1
                        continue

                    response.raise_for_status()
                    async for chunk in response.aiter_text():
                        if chunk:
                            callback(chunk)
                    elapsed = asyncio.get_event_loop().time() - start
                    self._logger.debug("stream finished (elapsed=%.2fs)", elapsed)
                    return
            except httpx.RequestError as exc:
                elapsed = asyncio.get_event_loop().time() - start
                self._logger.debug("stream request error (elapsed=%.2fs): %s", elapsed, repr(exc))
                if not self._should_retry_exception(attempt):
                    raise
                delay = self._compute_delay(attempt, None)
                self._log_retry(attempt, delay, error=repr(exc))
                await asyncio.sleep(delay)
                attempt += 1

    def _should_retry_response(self, response: httpx.Response, attempt: int) -> bool:
        if response.status_code not in _RETRY_STATUS:
            return False
        return attempt < int(self._max_retries)

    def _should_retry_exception(self, attempt: int) -> bool:
        return attempt < int(self._max_retries)

    def _compute_delay(self, attempt: int, response: Optional[httpx.Response]) -> float:
        retry_after = None
        if response is not None and getattr(response, "headers", None) is not None:
            retry_after = response.headers.get("Retry-After")
        if retry_after:
            delay = self._parse_retry_after(retry_after)
            if delay is not None:
                # cap retry-after to avoid overly long waits for interactive UIs
                return min(delay, self._max_backoff_seconds)
        base_delay = min(self._backoff_base * (2 ** attempt), self._max_backoff_seconds)
        jitter = random.uniform(0, base_delay * 0.25)
        return base_delay + jitter

    def _parse_retry_after(self, value: str) -> float | None:
        try:
            seconds = float(value)
            return max(seconds, 0.0)
        except ValueError:
            pass
        try:
            target = parsedate_to_datetime(value)
            if target is None:
                return None
            if target.tzinfo is None:
                target = target.replace(tzinfo=timezone.utc)
            delta = (target - datetime.now(timezone.utc)).total_seconds()
            return max(delta, 0.0)
        except (TypeError, ValueError):
            return None

    def _log_retry(
        self,
        attempt: int,
        delay: float,
        *,
        status: int | None = None,
        retry_after: str | None = None,
        error: str | None = None,
    ) -> None:
        self._logger.warning(
            "retrying request",
            extra={
                "attempt": attempt + 1,
                "delay": round(delay, 2),
                "status": status,
                "retry_after": retry_after,
                "api_key": redact_api_key(getattr(self._settings, "api_key", None)),
                "error": error,
            },
        )

# ----- end of patched class -----
