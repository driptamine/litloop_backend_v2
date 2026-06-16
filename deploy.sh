#!/bin/bash

# --- LitLoop Unified Deployment Script ---
# This script automates the deployment process on a GCP VM.

set -e

echo "🚀 Starting LitLoop Deployment..."

# 1. Environment Check
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with GCS_HMAC_ACCESS_KEY, GCS_HMAC_SECRET, etc."
    exit 1
fi

# 2. Update Code
echo "📥 Pulling latest changes..."
git pull origin main

# 3. Virtual Environment Setup
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# 4. Install/Update Dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements/base.txt

# 5. Database Migrations
echo "📂 Running database migrations..."
python manage.py migrate --noinput

# 6. Static Files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# 7. Pre-flight Check: GCS Connection
echo "🔍 Verifying GCS HMAC configuration..."
python manage.py shell -c "from django.conf import settings; import boto3; client=boto3.client('s3', endpoint_url='https://storage.googleapis.com', aws_access_key_id=settings.GCS_HMAC_ACCESS_KEY, aws_secret_access_key=settings.GCS_HMAC_SECRET); client.list_buckets(); print('✅ GCS HMAC Connection Verified!')" || { echo "❌ GCS HMAC Check Failed. Check your .env keys."; exit 1; }

# 8. Restart Services
echo "🚦 Restarting Gunicorn and Nginx..."
if systemctl is-active --quiet gunicorn; then
    sudo systemctl restart gunicorn
else
    echo "⚠️ Gunicorn service not found or not active. Skipping systemd restart."
fi

if systemctl is-active --quiet nginx; then
    sudo systemctl restart nginx
else
    echo "⚠️ Nginx service not found or not active. Skipping systemd restart."
fi

echo "✅ Deployment Successful!"
