#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting deployment..."

# Create swap space if it doesn't exist (crucial for e2-micro 1GB RAM)
if [ ! -f /swapfile ]; then
    echo "💾 Creating 2GB swap file..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Update and install necessary packages
echo "🔧 Updating and installing packages..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git libpq-dev

# Navigate to the project directory
cd /home/$USER/litloop_backend_v2

# Create virtual environment if not exists
echo "🐍 Setting up virtual environment..."
if [ ! -d "env" ]; then
  python3 -m venv env
fi
source env/bin/activate

# Upgrade pip and install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements/base.txt

# Run Django migrations
echo "📂 Running migrations..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Fix permissions for Nginx to access the socket
echo "🔑 Adjusting permissions for Nginx..."
chmod +x /home/$USER
chmod +x $(pwd)
chmod +x $(pwd)/deploy
chmod +x $(pwd)/deploy/gunicorn

# Set up Daphne (ASGI server for WebSocket support)
echo "🚦 Configuring Daphne..."
# Update WorkingDirectory and ExecStart in gunicorn.service if necessary
sed -i "s|/home/ubuntu/litloop_backend_v2|$(pwd)|g" deploy/gunicorn/gunicorn.service
sed -i "s|User=ubuntu|User=$USER|g" deploy/gunicorn/gunicorn.service
sudo cp deploy/gunicorn/gunicorn.service /etc/systemd/system/daphne.service
sudo systemctl daemon-reload
sudo systemctl enable daphne
sudo systemctl restart daphne

# Set up Nginx
echo "🌐 Configuring Nginx..."
# Update paths in nginx config if necessary
sed -i "s|/home/ubuntu/litloop_backend_v2|$(pwd)|g" deploy/nginx/django.conf
sudo cp deploy/nginx/django.conf /etc/nginx/sites-available/litloop.conf
sudo ln -sf /etc/nginx/sites-available/litloop.conf /etc/nginx/sites-enabled/litloop.conf
sudo nginx -t && sudo systemctl restart nginx

echo "✅ Deployment complete!"
