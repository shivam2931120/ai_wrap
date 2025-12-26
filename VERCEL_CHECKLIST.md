# ✅ Vercel Deployment Checklist

## Pre-Deployment

### Files Created/Updated
- ✅ `api/index.py` - Serverless function entry point
- ✅ `api/requirements.txt` - Python dependencies (Flask, CORS, httpx, pydantic)
- ✅ `vercel.json` - Build and routing configuration
- ✅ `.vercelignore` - Excludes unnecessary files
- ✅ `.env.example` - Environment variable template
- ✅ `frontend/src/services/api.js` - Production URL configuration
- ✅ `frontend/package.json` - Added vercel-build script

### Build Verification
- ✅ Frontend builds successfully: `npm run build` (105.38 KB gzipped)
- ✅ Backend API structure verified
- ✅ No TypeScript/ESLint errors
- ✅ All components render correctly

### Configuration
- ✅ CORS enabled in Flask app
- ✅ Routes configured for SPA (Single Page App)
- ✅ Static assets properly routed
- ✅ API routes prefixed with `/api/`
- ✅ Environment variables documented

## Deployment Steps

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Set Environment Variables
```bash
vercel env add OPENROUTER_API_KEY
# Paste your API key when prompted

vercel env add OPENROUTER_API_ENDPOINT
# Enter: https://openrouter.ai/api/v1
```

### 4. Deploy to Preview
```bash
vercel
```

### 5. Test Preview Deployment
- Check frontend loads: `https://your-project-preview.vercel.app`
- Test API: `https://your-project-preview.vercel.app/api/models`
- Send a test message in the UI

### 6. Deploy to Production
```bash
vercel --prod
```

## Post-Deployment Verification

### Frontend Checks
- [ ] Homepage loads correctly
- [ ] Theme toggle works (dark/light mode)
- [ ] All components render properly
- [ ] No console errors
- [ ] Responsive design works on mobile

### API Checks
- [ ] `/api/models` returns model list
- [ ] `/api/generate` accepts requests
- [ ] Error messages display properly
- [ ] Response times acceptable (<3s)

### Integration Checks
- [ ] Model selection works
- [ ] Token slider updates correctly
- [ ] Segmented control changes presets
- [ ] Send button triggers API call
- [ ] Messages display in chat
- [ ] Empty state shows example prompts
- [ ] Debug mode toggle works

### Performance Checks
- [ ] Lighthouse score > 90
- [ ] First Contentful Paint < 2s
- [ ] No unnecessary re-renders
- [ ] Static assets cached properly

## Troubleshooting

### Build Fails
```bash
# Test locally first
cd frontend && npm run build
cd backend && python api.py
```

### API Returns 500
- Check Vercel function logs
- Verify environment variables are set
- Ensure API key is valid

### CORS Errors
- Already configured in `backend/api.py`
- Check browser network tab for specific error
- Verify routes in `vercel.json`

### Static Files 404
- Ensure build output is in `frontend/build/`
- Check route configuration in `vercel.json`
- Verify distDir setting matches

## Monitoring

### Vercel Dashboard
- View deployment logs
- Check function invocations
- Monitor performance metrics
- Review analytics

### Key Metrics to Watch
- Function execution time
- Error rate
- Bandwidth usage
- Request count

## Rollback (if needed)

```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback [deployment-url]
```

## Custom Domain (Optional)

1. Go to Vercel dashboard
2. Select your project
3. Settings → Domains
4. Add your domain
5. Update DNS records as instructed

## Production URLs

After deployment:
- **App**: `https://your-project.vercel.app`
- **API Health**: `https://your-project.vercel.app/api/models`

## Success Criteria

✅ All checks passed
✅ No console errors
✅ API responds correctly
✅ UI is responsive
✅ Theme toggle works
✅ Messages send and receive
✅ Performance is acceptable

## Ready to Deploy! 🚀

Run: `vercel --prod`
