#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting deployment..."

# Update and install necessary packages
echo "🔧 Updating and installing packages..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx

# Ensure environment file is secure
echo "🔐 Setting permissions on environment file..."
chmod 600 /home/ubuntu/litloop_backend_v2/.env
chown ubuntu:ubuntu /home/ubuntu/litloop_backend_v2/.env

# Navigate to the project directory
cd /home/ubuntu/litloop_backend_v2

# Pull latest code
# echo "📥 Pulling latest code from main..."
# git pull origin main

# Create virtual environment if not exists
echo "🐍 Setting up virtual environment..."
if [ ! -d "env" ]; then
  python3 -m venv env
fi
source env/bin/activate

# Load environment variables from .env
echo "📦 Loading environment variables..."
set -a
source .env
set +a

# Upgrade pip and install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements/base.txt

# Run Django migrations
echo "📂 Running migrations..."
python manage.py migrate

# Set up Gunicorn
echo "🚦 Configuring Gunicorn..."
sudo cp deploy/gunicorn/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn

# Set up Nginx
echo "🌐 Configuring Nginx..."
sudo cp deploy/nginx/django.conf /etc/nginx/sites-available/litloop.conf
sudo ln -sf /etc/nginx/sites-available/litloop.conf /etc/nginx/sites-enabled/litloop.conf
sudo nginx -t && sudo systemctl restart nginx

echo "✅ Deployment complete!"
