"""Vercel serverless entry point for Ariary Numeric."""
import os
import sys
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Vercel sets VERCEL=1
os.environ.setdefault("VERCEL", "1")

import django
django.setup()

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
