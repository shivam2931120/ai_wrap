# gemini-wrapper

`gemini-wrapper` is a small, production-ready Python package that offers an extensible HTTP client for Gemini-style LLM APIs. It focuses on resilience, clean typing, and easy adaptation to any provider that speaks HTTP+JSON.

## Quickstart

1. Install dependencies (you can use `pip`, `pipx`, or Poetry):

```bash
pip install .[dev]
```

2. Create a `.env` file (optional) or export environment variables:

```bash
cat <<'EOF' > .env
GEMINI_API_KEY=your-api-key
GEMINI_API_ENDPOINT=https://generative.example.com
# Optional overrides
# GEMINI_TIMEOUT=30
# GEMINI_MAX_RETRIES=4
# GEMINI_PROJECT=my-project
EOF
```

The default paths assume generic REST endpoints (e.g., `/v1/complete`). Update them in code if your provider requires something different such as `/v1/models/<model>:generate`. Look for the `paths` configuration in `gemini_wrapper.config` or pass custom `EndpointPaths` to the client.

## Usage

### Async client (preferred)

```python
import asyncio
from gemini_wrapper.config import Settings, EndpointPaths
from gemini_wrapper.client import GeminiAsyncClient

async def main() -> None:
    settings = Settings.from_env(paths=EndpointPaths(
        complete="/v1/complete",  # Adjust to provider-specific path if needed
        chat="/v1/chat",
        embed="/v1/embed",
        stream_complete="/v1/stream",
    ))

    async with GeminiAsyncClient(settings=settings) as client:
        completion = await client.complete("Write a haiku about testing.")
        print(completion)

        chat_reply = await client.chat([
            {"role": "user", "content": "Summarise unit testing best practices."},
        ])
        print(chat_reply)

        embeddings = await client.embed(["First text", "Second text"])
        print(embeddings)

        await client.stream_complete(
            "Stream a list of prime numbers.",
            callback=lambda token: print(token, end="", flush=True),
        )

asyncio.run(main())
```

### Sync wrapper

```python
from gemini_wrapper.sync_client import GeminiClient

client = GeminiClient()
try:
    response = client.complete("Explain Python context managers.")
    print(response)
finally:
    client.close()
```

### CLI

The package installs a lightweight CLI named `gw` that proxies the `complete` call:

```bash
gw "Describe safe retry logic for HTTP clients."
```

Add `--json` to render raw JSON output.

### Health check

```python
async with GeminiAsyncClient() as client:
    await client.health_check()
```

## Streaming Example

```python
async def stream_example() -> None:
    async with GeminiAsyncClient() as client:
        def on_token(token: str) -> None:
            print(token, end="", flush=True)

        await client.stream_complete(
            "List Fibonacci numbers.",
            callback=on_token,
        )
```

## Testing

The project ships with `pytest` + `respx` tests. To run them:

```bash
pytest
```

## Notes

- All configuration values are environment-driven. Override via `Settings` if needed.
- Paths are intentionally generic; adjust `EndpointPaths` to match the provider (e.g., `/v1/models/text-bison-001:generate` for Google Gemini).
- Logging is structured and avoids leaking API keys.
