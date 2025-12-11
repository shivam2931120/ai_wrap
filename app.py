# app.py
"""
Minimal ChatGPT-like UI for Gemini wrapper (Gradio 6+).
Run: python app.py
"""

import asyncio
import logging
import os
import random
from typing import Any, Dict, List, Optional

import gradio as gr
import base64

# Try to find common async client exports in gemini_wrapper
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

log = logging.getLogger("gemini_ui")
logging.basicConfig(level=logging.INFO)

# ----------------- Minimal CSS (ChatGPT-like) -----------------
CUSTOM_CSS = r"""
:root {
  --bg: #0b0b0c;
  --panel: #0f1113;
  --muted: #94a3b8;
  --text: #e6eef8;
  --accent: #60a5fa;
  --bubble-user: linear-gradient(90deg,#2563eb,#1e40af);
  --bubble-assistant: rgba(255,255,255,0.03);
}

/* Page */
html, body { height:100%; margin:0; background:var(--bg); font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; color:var(--text); }

/* Centered narrow app */
.app-wrap {
  display:flex;
  justify-content:center;
  padding:28px 12px;
}
.app {
  width:780px;
  max-width:96%;
  display:flex;
  flex-direction:column;
  gap:14px;
}

/* Card */
.card {
  background:linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.00));
  border-radius:12px;
  padding:0;
  border: 1px solid rgba(255,255,255,0.04);
  box-shadow: 0 10px 30px rgba(2,6,23,0.6);
  overflow:hidden;
}

/* Conversation area */
.chat-area {
  height: 62vh;
  min-height: 360px;
  max-height: 72vh;
  overflow:auto;
  padding:18px;
  background: var(--panel);
  display:flex;
  flex-direction:column;
  gap:10px;
  scroll-behavior:smooth;
}

/* message bubbles (Gradio will render inside .chatbot) */
.msg-row { display:flex; width:100%; }
.msg-bubble {
  max-width:78%;
  padding:10px 12px;
  border-radius:12px;
  font-size:14px;
  line-height:1.5;
  color:var(--text);
  box-shadow: 0 1px 0 rgba(255,255,255,0.01) inset;
}

/* Sticky input area */
.input-area {
  display:flex;
  gap:12px;
  align-items:flex-end;
  padding:14px;
  background: linear-gradient(180deg, rgba(0,0,0,0.02), rgba(0,0,0,0.01));
  border-top:1px solid rgba(255,255,255,0.02);
}
.input-text {
  flex:1;
  min-height:48px;
  max-height:36vh;
  border-radius:10px;
  padding:12px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.03);
  color:var(--text) !important;
  resize:vertical;
  overflow:auto;
}
.send-btn {
  width:44px;
  height:44px;
  border-radius:999px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  background: linear-gradient(90deg, rgba(96,165,250,0.12), rgba(96,165,250,0.08));
  border: 1px solid rgba(96,165,250,0.16);
  color:var(--text);
  cursor:pointer;
  transition: transform .08s ease;
}
.send-btn:active { transform: translateY(1px); }

/* remove default focus outline on buttons, keep subtle focus on textarea */
button:focus, .send-btn:focus { outline:none; box-shadow:none; }

/* placeholder muted */
.input-text::placeholder { color: #97a0ad; }

/* Hide Gradio footer/attribution and bottom toolbar elements */
footer, .gradio-footer, .gradio-app__footer, .gradio-btm, .gradio-info, .gradio-credit, .built-with-gradio, .share-btns, .gradio-settings, .gradio-card__footer { display: none !important; }
.app a[href*="gradio"], .app a[href*="builtwith"] { display: none !important; }
"""

# ----------------- JS to set title and copy buttons -----------------
# NUCLEAR title override: hijack document.title property so NOTHING can change it
TITLE_AND_COPY_JS = r"""
<script>
(function(){
  const TITLE = "EchoAI";
  
  // 1. Hijack document.title property completely
  try {
    Object.defineProperty(document, 'title', {
      get: function() { return TITLE; },
      set: function(v) { /* ignored */ },
      configurable: false
    });
  } catch(e) {
    // If instance fails, try prototype
    try {
      Object.defineProperty(Document.prototype, 'title', {
        get: function() { return TITLE; },
        set: function(v) { /* ignored */ },
        configurable: false
      });
    } catch(e2) {}
  }
  
  // 2. Force <title> element content
  function forceTitle() {
    try {
      let titleEl = document.querySelector('title');
      if (!titleEl) {
        titleEl = document.createElement('title');
        document.head.appendChild(titleEl);
      }
      if (titleEl.textContent !== TITLE) {
        titleEl.textContent = TITLE;
      }
    } catch(e) {}
  }
  
  // 3. Apply immediately and watch for changes
  forceTitle();
  
  // 4. Observer on <head> and <title>
  try {
    const obs = new MutationObserver(forceTitle);
    obs.observe(document.head || document.documentElement, {
      childList: true,
      subtree: true,
      characterData: true,
      characterDataOldValue: true
    });
  } catch(e) {}
  
  // 5. Aggressive interval (persists forever)
  setInterval(forceTitle, 100);
  
  // 6. Hook all possible title-setting events
  ['load', 'DOMContentLoaded', 'readystatechange', 'pageshow'].forEach(evt => {
    window.addEventListener(evt, forceTitle, true);
  });
  
  // 7. Copy buttons for assistant messages
  (function addCopyButtons(){
    function tryAdd(){
      const messages = document.querySelectorAll(".chatbot .message");
      messages.forEach(msg=>{
        if (!msg.classList.contains("assistant")) return;
        if (msg.dataset.copyAttached) return;
        const val = msg.querySelector(".value");
        if (!val) return;
        const btn = document.createElement("button");
        btn.innerText = "⧉";
        btn.title = "Copy";
        btn.style.marginLeft = "6px";
        btn.style.background = "transparent";
        btn.style.border = "1px solid rgba(255,255,255,0.04)";
        btn.style.color = "inherit";
        btn.style.borderRadius = "6px";
        btn.style.padding = "4px";
        btn.onclick = (e)=> {
          e.stopPropagation();
          const text = val.innerText || val.textContent || "";
          if (!text) return;
          navigator.clipboard?.writeText(text);
          btn.innerText = "✓";
          setTimeout(()=> btn.innerText = "⧉", 1200);
        };
        msg.appendChild(btn);
        msg.dataset.copyAttached = "1";
      });
    }
    const obs = new MutationObserver(tryAdd);
    obs.observe(document.body, { childList:true, subtree:true });
    setTimeout(tryAdd, 500);
  })();
  
})();
</script>
"""

# tiny default favicon (1x1 PNG) base64 — will be written to `echoai.png` if missing
ECHOAI_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAA"
    "ASUVORK5CYII="
)

# ----------------- Client helper (keeps your integration) -----------------
_gemini_client = None


def get_client():
    """Instantiate and return the async client or raise clear error."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    if GeminiClientAsync is None:
        raise RuntimeError(
            "Could not find an async Gemini client in the package 'gemini_wrapper'. "
            "Ensure your package is installed and exports AsyncGeminiClient or GeminiAsyncClient. "
            "Install with: pip install gemini-wrapper"
        )
    try:
        _gemini_client = GeminiClientAsync()
    except TypeError:
        raise RuntimeError(
            "Failed to instantiate Gemini client with no arguments. "
            "If your wrapper requires configuration, update get_client() to pass the required args."
        )
    return _gemini_client


def extract_text(response: Any) -> str:
    """Attempt to pull a human string out of typical API responses."""
    try:
        if response is None:
            return ""
        if isinstance(response, str):
            return response
        if isinstance(response, dict):
            # Google-style
            c = response.get("candidates")
            if isinstance(c, list) and c:
                parts = c[0].get("content", {}).get("parts")
                if isinstance(parts, list):
                    return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in parts)
            # OpenAI-style
            choices = response.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    return first.get("text") or first.get("message", {}).get("content") or str(first)
            # output field
            if "output" in response:
                out = response.get("output")
                return out if isinstance(out, str) else str(out)
        return str(response)
    except Exception:
        return str(response)


async def generate(prompt: str, model: Optional[str] = None, max_tokens: Optional[int] = None) -> str:
    """
    Call client's complete() with small retries for transient issues.
    Supports either async or sync `complete`.
    """
    if not prompt or not prompt.strip():
        return ""

    max_attempts = 3
    base_delay = 0.6

    for attempt in range(1, max_attempts + 1):
        try:
            client = get_client()
            complete_fn = getattr(client, "complete", None)
            if complete_fn is None:
                raise RuntimeError("Gemini client missing a 'complete' method.")

            # try to pass model/max_tokens if accepted
            if asyncio.iscoroutinefunction(complete_fn):
                if _accepts_args(complete_fn):
                    raw = await complete_fn(prompt, model=model, max_tokens=max_tokens)
                else:
                    raw = await complete_fn(prompt)
            else:
                loop = asyncio.get_running_loop()

                def _sync_call():
                    if _accepts_args(complete_fn):
                        return complete_fn(prompt, model=model, max_tokens=max_tokens)
                    return complete_fn(prompt)

                raw = await loop.run_in_executor(None, _sync_call)

            return extract_text(raw)
        except Exception as e:
            # check rate limit like patterns
            msg = str(e)
            is_429 = "429" in msg or getattr(getattr(e, "response", None), "status_code", None) == 429
            is_server_err = getattr(getattr(e, "response", None), "status_code", None) in (502, 503, 504)
            if is_429 or is_server_err:
                wait = min(30.0, base_delay * (2 ** (attempt - 1))) + random.random()
                log.warning("Transient error; backing off %.2fs (attempt %d/%d) — %s", wait, attempt, max_attempts, msg[:200])
                await asyncio.sleep(wait)
                continue
            log.exception("Non-retryable generation error")
            return f"Error: {e}"
    return "Error: rate limited or unavailable — please try again later"


def _accepts_args(fn) -> bool:
    try:
        import inspect

        sig = inspect.signature(fn)
        return any(n in sig.parameters for n in ("model", "max_tokens"))
    except Exception:
        return False


# ----------------- History normalization & chat_turn -----------------
def normalize_to_messages(history: List[Any]) -> List[Dict[str, str]]:
    if not history:
        return []
    out: List[Dict[str, str]] = []
    if all(isinstance(item, (list, tuple)) and len(item) == 2 for item in history):
        for u, a in history:
            out.append({"role": "user", "content": str(u)})
            out.append({"role": "assistant", "content": str(a)})
        return out
    for item in history:
        if isinstance(item, dict) and "role" in item and "content" in item:
            out.append({"role": str(item["role"]), "content": str(item["content"])})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            out.append({"role": "user", "content": str(item[0])})
            out.append({"role": "assistant", "content": str(item[1])})
        else:
            out.append({"role": "assistant", "content": str(item)})
    return out


async def chat_turn(prompt: str, chat_history: List[Dict[str, str]], model: str, max_tokens: int):
    history = normalize_to_messages(chat_history or [])
    if not prompt or not prompt.strip():
        return "", history

    history.append({"role": "user", "content": prompt})
    history.append({"role": "assistant", "content": "Thinking..."})

    reply = await generate(prompt, model=model if model and model != "(default)" else None, max_tokens=max_tokens or None)

    if history and history[-1]["content"] == "Thinking...":
        history[-1]["content"] = reply
    else:
        history.append({"role": "assistant", "content": reply})

    return "", history


# ----------------- Build UI -----------------
def create_ui():
    with gr.Blocks(title="EchoAI") as app:
        # wrapper HTML open
        gr.HTML("<div class='app-wrap'><div class='app'>", elem_id="app_open")

        # small top area (logo + title) - optional minimalist

        # main card (chat + input)
        with gr.Row(elem_classes="card", variant="compact"):
            with gr.Column(scale=1):
                # Chatbot (use messages dict format)
                chatbot = gr.Chatbot(label="", elem_classes="chat-area", value=[])

                # hidden controls (kept to maintain function signature)
                model_select = gr.Dropdown(
                    choices=["(default)", "gemini-pro", "gemini-1.5", "flash"],
                    value="(default)",
                    label="Model",
                    interactive=True,
                    visible=False,
                )
                max_tokens = gr.Slider(minimum=16, maximum=1024, step=16, value=256, label="Max tokens", interactive=True, visible=False)

                # prompt textbox and buttons
                prompt = gr.Textbox(
                    placeholder="Type your message and press Enter — shift+Enter for newline",
                    lines=2,
                    elem_classes="input-text",
                    show_label=False,
                )

                with gr.Row(elem_classes="input-area", variant="compact"):
                    send_btn = gr.Button(value="→", elem_classes="send-btn")
                    clear_btn = gr.Button(value="Clear", elem_classes="msg-action-btn")

        # close wrapper HTML
        gr.HTML("</div></div>", elem_id="app_close")

        # inject title + copy JS
        gr.HTML(TITLE_AND_COPY_JS)

        # Wire events AFTER the components exist (no undefined-variable warnings)
        prompt.submit(fn=chat_turn, inputs=[prompt, chatbot, model_select, max_tokens], outputs=[prompt, chatbot])
        send_btn.click(fn=chat_turn, inputs=[prompt, chatbot, model_select, max_tokens], outputs=[prompt, chatbot])

        def _clear():
            return "", []
        clear_btn.click(fn=_clear, inputs=[], outputs=[prompt, chatbot])

    return app


def main():
    app = create_ui()
    try:
        if not os.path.exists("echoai.png"):
            with open("echoai.png", "wb") as f:
                f.write(base64.b64decode(ECHOAI_PNG_B64))
    except Exception:
        pass

    port = int(os.environ.get("PORT", "7860"))

    launch_kwargs = dict(server_name="0.0.0.0", server_port=port, show_error=True, share=False, favicon_path="echoai.png", css=CUSTOM_CSS)

    app.launch(**launch_kwargs)

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        log.error("Startup error: %s", e)
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        log.exception("Unexpected error during startup")
        print(f"Unexpected error: {e}")
        exit(1)
