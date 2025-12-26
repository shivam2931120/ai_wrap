# Vercel Deployment Guide for EchoAI

## Prerequisites

1. Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm install -g vercel`
3. API keys ready (OpenRouter or Gemini)

## Setup Steps

### 1. Environment Variables

In Vercel dashboard, add these environment variables:

```
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_API_ENDPOINT=https://openrouter.ai/api/v1
```

Or via CLI:
```bash
vercel env add OPENROUTER_API_KEY
vercel env add OPENROUTER_API_ENDPOINT
```

### 2. Deploy

#### Option A: Deploy via CLI
```bash
# From project root
vercel

# For production
vercel --prod
```

#### Option B: Deploy via Git
1. Push to GitHub
2. Import project in Vercel dashboard
3. Vercel will auto-deploy

### 3. Configuration

The project is configured with:
- **Frontend**: React app built as static site
- **Backend**: Flask API as serverless functions
- **Routes**: 
  - `/api/*` → serverless functions
  - `/*` → frontend static files

## Project Structure

```
ai_wrap/
├── api/
│   ├── index.py          # Vercel serverless entry
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── build/            # Production build
│   ├── src/
│   └── package.json
├── backend/
│   └── api.py           # Flask app
├── gemini_wrapper/      # API client
└── vercel.json          # Vercel config
```

## Testing Locally

### Backend
```bash
cd backend
python api.py
```

### Frontend
```bash
cd frontend
npm start
```

## Troubleshooting

### Build Fails
- Check frontend builds locally: `cd frontend && npm run build`
- Verify Python dependencies in `api/requirements.txt`

### API Not Working
- Verify environment variables are set in Vercel
- Check serverless function logs in Vercel dashboard
- Ensure API routes start with `/api/`

### CORS Issues
- CORS is configured in Flask app
- Vercel routes handle SPA correctly

## URLs After Deployment

- Production: `https://your-project.vercel.app`
- API: `https://your-project.vercel.app/api/models`
- Frontend: `https://your-project.vercel.app`

## Custom Domain

Add in Vercel dashboard:
1. Go to project settings
2. Domains section
3. Add your domain
4. Update DNS records as instructed

## Monitoring

- View logs: Vercel dashboard → Functions tab
- Analytics: Vercel dashboard → Analytics
- Performance: Built-in Web Vitals tracking
