# LitLoop Backend

LitLoop is a powerful Django-based backend for a multimedia social platform, featuring real-time messaging, video transcoding, and seamless cloud integration.

## 🛠 Tech Stack

- **Framework:** Django 3.9 (ASGI with Channels)
- **Web Server:** Daphne (ASGI), Nginx (Proxy)
- **Database:** PostgreSQL (Local) / Neon (Production)
- **Real-time:** Redis (Channel Layers)
- **Task Queue:** Celery + RabbitMQ/Redis
- **Storage:** Google Cloud Storage (HMAC)
- **Media:** FFmpeg / Bento4 (HLS Transcoding)

---

## 💻 Local Development

### 1. Prerequisites
- Python 3.9
- PostgreSQL
- Redis
- Nginx

### 2. Setup
```bash
# Clone the repository
git clone <repo_url>
cd litloop_backend

# Create virtual environment
python3 -m venv venv_3.9
source venv_3.9/bin/activate

# Install dependencies
pip install -r requirements/base.txt
```

### 3. Environment Configuration
Create a `.env` file in the root:
```ini
DJANGO_SETTINGS_MODULE=litloop_project.settings.dev
DB_NAME=litloop_db_dev
DB_USER=postgres
DB_PASSWORD=your_password
REDIS_LOCATION=redis://127.0.0.1:6379/1
```

### 4. Running the Project
```bash
# Apply migrations
python manage.py migrate

# Start the server (handles HTTP & WebSockets)
python manage.py runserver
```

---

## 🚀 Production Deployment

### Infrastructure
- **Server:** GCP VM (EC2-style)
- **OS User:** `driptamine`
- **Path:** `/home/driptamine/litloop_backend_v2`

### Deployment Workflow
The project uses **GitHub Actions** for CI/CD.
1. Push changes to the `main` branch.
2. The `deploy.yml` workflow SSHs into the server as `ubuntu`.
3. It pulls the latest code, installs requirements, and migrates the database.
4. It updates the `daphne` service and restarts Nginx.

### Manual Service Management
```bash
# Check Daphne (WebSocket + HTTP server)
sudo systemctl status gunicorn

# Check Nginx
sudo systemctl status nginx

# View Logs
sudo journalctl -u gunicorn -f
```

---

## 🏗 Architecture Notes

### WebSocket Authentication
WebSockets are authenticated via JWT in the query string:
`ws://localhost:8000/ws/chat/<chat_id>/?token=<JWT_TOKEN>`

The `JWTAuthMiddleware` handles token decoding and populates `scope['user']`.

### Database Routing
- **Local:** Uses standard PostgreSQL on localhost.
- **Production:** Uses Neon PostgreSQL.
- **Neon Fix:** The `base.py` settings include a sanitizer for `DATABASE_URL` to handle specific Neon SNI/Endpoint ID requirements and prevent channel binding errors.

### Media Processing
Videos are transcoded into HLS chunks using FFmpeg and Bento4 for adaptive bitrate streaming.

---

## 📂 Directory Structure
- `litloop_project/`: Core settings and ASGI/WSGI config.
- `chats/`: WebSocket consumers and chat logic.
- `users/`: Custom user model and JWT authentication.
- `deploy/`: Nginx, Systemd, and Docker configuration files.
- `uploader/`: Media upload and transcoding handlers.
