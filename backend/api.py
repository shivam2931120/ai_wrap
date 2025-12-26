"""
Flask backend API for EchoAI
"""
import asyncio
import logging
import time
import json
from typing import Any, Dict, List, Optional, Tuple
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Try to find async client
GeminiClientAsync = None
try:
    from gemini_wrapper import AsyncGeminiClient as GeminiClientAsync
except Exception:
    try:
        from gemini_wrapper import GeminiAsyncClient as GeminiClientAsync
    except Exception:
        try:
            from gemini_wrapper.client import AsyncGeminiClient as GeminiClientAsync
        except Exception:
            try:
                from gemini_wrapper.client import GeminiAsyncClient as GeminiClientAsync
            except Exception:
                GeminiClientAsync = None

log = logging.getLogger("echoai")
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Models Configuration
MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-flash-1.5:free",
    "mistralai/mistral-7b-instruct:free",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-mini",
    "google/gemini-pro-1.5",
    "meta-llama/llama-3.1-70b-instruct",
    "openai/gpt-4o",
    "anthropic/claude-3-opus",
]

_client = None

def get_client():
    """Get or create the OpenRouter client."""
    global _client
    if _client is not None:
        return _client
    
    if GeminiClientAsync is None:
        raise RuntimeError("Could not find async client in 'gemini_wrapper'.")
    
    try:
        from gemini_wrapper.config import Settings
        settings = Settings.from_env()
        _client = GeminiClientAsync(settings=settings)
        return _client
    except Exception as e:
        raise RuntimeError(f"Failed to instantiate client: {e}")

def extract_text(response: Any) -> str:
    """Extract text from OpenRouter API response."""
    try:
        if response is None:
            return ""
        if isinstance(response, str):
            return response
        if isinstance(response, dict):
            choices = response.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    message = first.get("message")
                    if isinstance(message, dict):
                        content = message.get("content")
                        if content:
                            return str(content)
                    text = first.get("text")
                    if text:
                        return str(text)
            if "output" in response:
                return str(response["output"])
        return str(response)
    except Exception:
        return str(response)

def parse_error_message(error: Exception) -> Tuple[str, str, Optional[str]]:
    """Parse error into user-friendly message."""
    error_str = str(error)
    
    if "404" in error_str or "Not Found" in error_str:
        return ("Model Not Found", "The selected model is not available. Try choosing a different model.", "404")
    elif "401" in error_str or "Unauthorized" in error_str:
        return ("Authentication Failed", "Your API key is invalid or expired. Please check your configuration.", "401")
    elif "403" in error_str or "Forbidden" in error_str:
        return ("Access Denied", "You don't have permission to use this model. Check your API plan.", "403")
    elif "429" in error_str or "rate limit" in error_str.lower():
        return ("Rate Limit Exceeded", "Too many requests. Please wait a moment and try again.", "429")
    elif "500" in error_str or "502" in error_str or "503" in error_str:
        return ("Server Error", "The API is temporarily unavailable. Please try again in a moment.", "5xx")
    elif "timeout" in error_str.lower():
        return ("Request Timeout", "The request took too long. Try using a shorter prompt or different model.", "Timeout")
    else:
        return ("Request Failed", "An unexpected error occurred. Please try again.", None)

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models."""
    return jsonify({"models": MODELS})

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate a response from the API."""
    data = request.json
    prompt = data.get('prompt', '')
    model = data.get('model', MODELS[0])
    max_tokens = data.get('max_tokens', 1024)
    show_debug = data.get('show_debug', False)
    
    if not prompt or not prompt.strip():
        return jsonify({"error": "Prompt is required"}), 400
    
    start_time = time.time()
    
    try:
        client = get_client()
        kwargs = {"model": model, "max_tokens": max_tokens}
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        raw = loop.run_until_complete(client.complete(prompt, **kwargs))
        loop.close()
        
        latency_ms = (time.time() - start_time) * 1000
        response_text = extract_text(raw)
        
        result = {
            "response": response_text,
            "latency_ms": latency_ms,
            "tokens": len(response_text) // 4  # Rough estimation
        }
        
        if show_debug:
            result["debug"] = {
                "request": {"model": model, "max_tokens": max_tokens},
                "response": raw
            }
        
        return jsonify(result)
        
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        log.exception("Generation error")
        
        title, message, code = parse_error_message(e)
        
        return jsonify({
            "error": True,
            "title": title,
            "message": message,
            "code": code,
            "latency_ms": latency_ms
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", "5000"))
    app.run(host='0.0.0.0', port=port, debug=False)
