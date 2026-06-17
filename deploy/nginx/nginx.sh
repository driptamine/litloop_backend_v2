#!/bin/bash
set -e

# Update package list and install Nginx
sudo apt update
sudo apt install -y nginx

# Write Nginx config for your app
cat <<EOF | sudo tee /etc/nginx/sites-available/litloop
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site by symlinking
sudo ln -sf /etc/nginx/sites-available/litloop /etc/nginx/sites-enabled/litloop

# Test Nginx config
sudo nginx -t

# Restart Nginx to apply changes
sudo systemctl restart nginx

# Enable nginx to start on boot
sudo systemctl enable nginx

echo "Nginx setup completed."
