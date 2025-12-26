#!/bin/bash

echo "🚀 EchoAI - Vercel Deployment Script"
echo "===================================="
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found"
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

echo "✅ Vercel CLI ready"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found"
    echo "📝 Please create .env with your API keys"
    echo ""
    echo "Required variables:"
    echo "  OPENROUTER_API_KEY=your_key_here"
    echo "  OPENROUTER_API_ENDPOINT=https://openrouter.ai/api/v1"
    echo ""
    exit 1
fi

echo "✅ Environment file found"
echo ""

# Test frontend build
echo "🔨 Testing frontend build..."
cd frontend
npm run build > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Frontend builds successfully"
else
    echo "❌ Frontend build failed"
    echo "Run 'cd frontend && npm run build' to see errors"
    exit 1
fi

cd ..
echo ""

# Show deployment options
echo "📋 Deployment Options:"
echo ""
echo "1. Preview deployment (test first):"
echo "   vercel"
echo ""
echo "2. Production deployment:"
echo "   vercel --prod"
echo ""
echo "⚠️  Make sure to set environment variables in Vercel:"
echo "   vercel env add OPENROUTER_API_KEY"
echo "   vercel env add OPENROUTER_API_ENDPOINT"
echo ""

read -p "Deploy to production now? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying to production..."
    vercel --prod
else
    echo "Skipped. Run 'vercel --prod' when ready."
fi
