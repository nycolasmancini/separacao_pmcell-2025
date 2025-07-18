#!/usr/bin/env python
"""Main entry point for Railway deployment"""
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the FastAPI app
from app.main import app

# This allows Railway to find the app
__all__ = ['app']