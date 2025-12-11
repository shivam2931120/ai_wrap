"""Command line interface for gemini-wrapper."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from .sync_client import GeminiClient


def _render_output(payload: Dict[str, Any]) -> str:
    # Try to extract text from Gemini response format
    if "candidates" in payload and len(payload["candidates"]) > 0:
        candidate = payload["candidates"][0]
        if "content" in candidate and "parts" in candidate["content"]:
            parts = candidate["content"]["parts"]
            if len(parts) > 0 and "text" in parts[0]:
                return parts[0]["text"]
    
    # Fallback to generic extraction
    if "text" in payload and isinstance(payload["text"], str):
        return payload["text"]
    if "completion" in payload and isinstance(payload["completion"], str):
        return payload["completion"]
    return json.dumps(payload, indent=2, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Call Gemini-style completion endpoints from the terminal.")
    parser.add_argument("prompt", help="Prompt to send to the completion endpoint.")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Return raw JSON output.")

    args = parser.parse_args()

    client = GeminiClient()
    try:
        response = client.complete(args.prompt)
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        client.close()

    if args.as_json:
        print(json.dumps(response, indent=2, sort_keys=True))
    else:
        print(_render_output(response))


if __name__ == "__main__":
    main()
