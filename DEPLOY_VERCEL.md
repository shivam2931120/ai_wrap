# EchoAI - Quick Vercel Deploy

## One-Command Deploy

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Deploy from project root
vercel
```

## Set Environment Variables

Before deploying, add your API key:

```bash
vercel env add OPENROUTER_API_KEY
# Enter your API key when prompted

vercel env add OPENROUTER_API_ENDPOINT
# Enter: https://openrouter.ai/api/v1
```

## Deploy to Production

```bash
vercel --prod
```

## What Happens

1. **Frontend** builds automatically from `frontend/` directory
2. **Backend** deploys as serverless functions from `api/` directory
3. Routes are configured to:
   - Send `/api/*` requests to serverless functions
   - Serve frontend static files for all other routes

## Access Your App

After deployment, Vercel provides a URL:
- **Your App**: `https://your-project.vercel.app`
- **API Health**: `https://your-project.vercel.app/api/models`

## Project Structure (Vercel-Ready)

```
ai_wrap/
├── api/
│   ├── index.py              # Serverless entry point
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/                  # React source
│   ├── public/               # Static assets
│   └── package.json          # Contains vercel-build script
├── backend/
│   └── api.py               # Flask app (imported by api/index.py)
├── gemini_wrapper/          # API client library
└── vercel.json              # Deployment configuration
```

## Key Files for Vercel

### vercel.json
Configures builds and routes. No changes needed.

### api/index.py
Serverless function entry point. Imports Flask app from `backend/api.py`.

### frontend/package.json
Contains `vercel-build` script for automatic frontend builds.

### .vercelignore
Excludes unnecessary files from deployment (dev files, docs, etc.).

## Troubleshooting

**Build fails?**
```bash
# Test frontend build locally
cd frontend && npm run build

# Test backend locally
cd backend && python api.py
```

**API not working?**
- Check environment variables in Vercel dashboard
- View function logs in Vercel dashboard → Functions

**CORS errors?**
- Already configured in Flask app
- Check browser console for specific error

## Local Development

Backend:
```bash
cd backend
python api.py
```

Frontend (in another terminal):
```bash
cd frontend
npm start
```

## Need Help?

See [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md) for detailed instructions.
