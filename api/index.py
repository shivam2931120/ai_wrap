"""
Vercel serverless function for API routes
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.api import app

# Export the app for Vercel
handler = app
