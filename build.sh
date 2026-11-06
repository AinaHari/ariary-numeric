#!/bin/bash
# Vercel build script
cd backend
python manage.py collectstatic --noinput
python manage.py migrate --noinput