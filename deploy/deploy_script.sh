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
sudo touch /var/log/nginx/ws_access.log
sudo chown www-data:www-data /var/log/nginx/ws_access.log
chmod +x /home/$USER
chmod +x $(pwd)
chmod +x $(pwd)/deploy
chmod +x $(pwd)/deploy/gunicorn

# Set up Daphne (ASGI server for WebSocket support)
echo "🚦 Configuring Daphne (WebSockets)..."
sed -i "s|/home/driptamine/litloop_backend_v2|$(pwd)|g" deploy/gunicorn/gunicorn.service
sed -i "s|User=driptamine|User=$USER|g" deploy/gunicorn/gunicorn.service
sudo cp deploy/gunicorn/gunicorn.service /etc/systemd/system/daphne.service

# Set up Gunicorn (WSGI server for HTTP performance)
echo "🚦 Configuring Gunicorn (HTTP)..."
sed -i "s|/home/driptamine/litloop_backend_v2|$(pwd)|g" deploy/gunicorn/gunicorn_http.service
sed -i "s|User=driptamine|User=$USER|g" deploy/gunicorn/gunicorn_http.service
sudo cp deploy/gunicorn/gunicorn_http.service /etc/systemd/system/gunicorn_http.service

sudo systemctl daemon-reload
sudo systemctl enable daphne gunicorn_http
sudo systemctl restart daphne gunicorn_http

# Add handy aliases (idempotent)
grep -q "alias guni=" ~/.bashrc 2>/dev/null || echo "alias guni='sudo systemctl restart gunicorn_http && sudo systemctl status gunicorn_http'" >> ~/.bashrc
grep -q "alias daph=" ~/.bashrc 2>/dev/null || echo "alias daph='sudo systemctl restart daphne && sudo systemctl status daphne'" >> ~/.bashrc

# Set up Nginx
echo "🌐 Configuring Nginx..."
# Update paths in nginx config if necessary
sed -i "s|/home/driptamine/litloop_backend_v2|$(pwd)|g" deploy/nginx/django.conf
sudo cp deploy/nginx/django.conf /etc/nginx/sites-available/litloop.conf
sudo ln -sf /etc/nginx/sites-available/litloop.conf /etc/nginx/sites-enabled/litloop.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo "✅ Deployment complete!"
