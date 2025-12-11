# Deploying this Gradio app to Vercel (Docker)

This repository contains a Gradio app (`app.py`). Vercel can deploy this project using the provided `Dockerfile`.

Quick steps (local):

1. Install and log in with the Vercel CLI:

```bash
npm i -g vercel
vercel login
```

2. Build & test locally with Docker (optional):

```bash
# build
docker build -t gemini-gradio:local .
# run
docker run -p 7860:7860 gemini-gradio:local
# then open http://localhost:7860
```

3. Deploy to Vercel using Docker builder:

```bash
# from repo root
vercel --prod
```

Important notes:
- The app reads the `PORT` environment variable and will listen on that port (Vercel provides a port).
- If your app depends on any secret API keys (e.g. `GEMINI_API_KEY`), set them in the Vercel Dashboard under the Project > Settings > Environment Variables.
- The `Dockerfile` installs dependencies from `requirements.txt`. Update that file if you add libraries.

Troubleshooting:
- If Vercel fails to find a free port, ensure the Dockerfile exposes `7860` and the app reads `PORT` (already configured).
- For large model usage or heavy concurrency, consider a platform that supports long-running CPU/GPU instances (e.g. Render, Fly, Railway, or a VM provider).

