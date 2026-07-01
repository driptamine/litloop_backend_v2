import os


# ─── OAUTH ─────────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_SECRET_KEY")
VK_CLIENT_ID = os.environ.get("VK_CLIENT_ID")
VK_CLIENT_SECRET = os.environ.get("VK_CLIENT_SECRET")
VK_OAUTH_REDIRECT_URI = os.environ.get("VK_OAUTH_REDIRECT_URI", "http://localhost:3001/auth/vk/callback")
