"""
Configuration module for Content Publisher
"""

import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Database
DATABASE_PATH = os.path.join(DATA_DIR, "app.db")

# Ensure directories exist
for d in [DATA_DIR, OUTPUT_DIR, UPLOAD_DIR]:
    os.makedirs(d, exist_ok=True)

# Flask settings
SECRET_KEY = os.environ.get("SECRET_KEY", "content-publisher-secret-key-change-me")
DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"

# ═══════════════════════════════════════════════════════════
#  SOCIAL MEDIA API CREDENTIALS
#  Set these in your .env file or environment variables
# ═══════════════════════════════════════════════════════════

# YouTube / Google OAuth
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REDIRECT_URI = os.environ.get("YOUTUBE_REDIRECT_URI", "http://localhost:5000/auth/youtube/callback")
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

# TikTok OAuth
TIKTOK_CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "")
TIKTOK_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "")
TIKTOK_REDIRECT_URI = os.environ.get("TIKTOK_REDIRECT_URI", "http://localhost:5000/auth/tiktok/callback")
TIKTOK_SCOPES = ["video.publish", "video.list"]

# Instagram / Facebook OAuth
FACEBOOK_APP_ID = os.environ.get("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET = os.environ.get("FACEBOOK_APP_SECRET", "")
FACEBOOK_REDIRECT_URI = os.environ.get("FACEBOOK_REDIRECT_URI", "http://localhost:5000/auth/facebook/callback")
INSTAGRAM_SCOPES = ["instagram_basic", "instagram_content_publish", "pages_show_list", "pages_read_engagement"]
FACEBOOK_SCOPES = ["pages_manage_posts", "pages_read_engagement", "video_upload"]

# OAuth URL templates
YOUTUBE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize"
FACEBOOK_AUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
