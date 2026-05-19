"""
Content Publisher — Main Flask Application
TTS Generation + Social Media Video Publishing
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from werkzeug.utils import secure_filename

from config import (
    BASE_DIR, OUTPUT_DIR, UPLOAD_DIR, DATABASE_PATH, SECRET_KEY, DEBUG,
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REDIRECT_URI, YOUTUBE_SCOPES, YOUTUBE_AUTH_URL,
    TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI, TIKTOK_AUTH_URL,
    FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_REDIRECT_URI, FACEBOOK_AUTH_URL,
    INSTAGRAM_SCOPES, FACEBOOK_SCOPES,
)
from models import init_db, save_tts_record, get_tts_history, save_publish_record, get_publish_history
from tts_engine import VOICES, PRESETS, generate_tts
from social_publisher import (
    PLATFORMS, get_platforms_config, get_platform_fields,
    get_accounts, get_account_by_platform, save_account, delete_account,
    publish_video,
)


# ═══════════════════════════════════════════════════════════
#  APP SETUP
# ═══════════════════════════════════════════════════════════

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB max upload

# Initialize database
init_db()


# ═══════════════════════════════════════════════════════════
#  ROUTES — PAGES
# ═══════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Home page — TTS Generator."""
    return render_template("index.html", voices=VOICES, presets=PRESETS, tts_history=get_tts_history(10))


@app.route("/publish")
def publish_page():
    """Video publishing page."""
    return render_template(
        "publish.html",
        platforms=PLATFORMS,
        accounts=get_accounts(DATABASE_PATH),
        publish_history=get_publish_history(10),
    )


# ═══════════════════════════════════════════════════════════
#  API — TTS
# ═══════════════════════════════════════════════════════════

@app.route("/api/tts/generate", methods=["POST"])
def api_tts_generate():
    """Generate TTS audio from text."""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        voice_key = data.get("voice", "1")
        preset_key = data.get("preset", "documentary")
        filename = data.get("filename", "").strip()

        if not prompt:
            return jsonify({"success": False, "error": "Please enter your script text"})

        result = generate_tts(prompt, voice_key, preset_key, filename, OUTPUT_DIR)

        if result.get("success"):
            # Save to history
            save_tts_record(
                filename=result["filename"],
                voice_name=result["voice"],
                preset_name=result["preset"],
                prompt_preview=prompt[:200],
                file_path=result["file_path"],
                file_size_kb=result.get("size_kb", 0),
            )

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/tts/download/<filename>")
def api_tts_download(filename):
    """Download a generated TTS audio file."""
    file_path = os.path.join(OUTPUT_DIR, secure_filename(filename))
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    return jsonify({"error": "File not found"}), 404


@app.route("/api/tts/history")
def api_tts_history():
    """Get TTS generation history."""
    return jsonify(get_tts_history())


@app.route("/api/tts/voices")
def api_tts_voices():
    """Get available voices."""
    return jsonify(VOICES)


@app.route("/api/tts/presets")
def api_tts_presets():
    """Get available presets."""
    return jsonify(PRESETS)


# ═══════════════════════════════════════════════════════════
#  API — VIDEO UPLOAD
# ═══════════════════════════════════════════════════════════

@app.route("/api/video/upload", methods=["POST"])
def api_video_upload():
    """Upload a video file."""
    if "video" not in request.files:
        return jsonify({"success": False, "error": "No video file provided"})

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"})

    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        return jsonify({"success": False, "error": f"Unsupported format: {ext}. Allowed: {', '.join(allowed_extensions)}"})

    filename = secure_filename(file.filename)
    # Add timestamp to avoid conflicts
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{filename}"

    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    return jsonify({
        "success": True,
        "filename": filename,
        "file_path": file_path,
        "size_mb": round(file_size_mb, 2),
    })


# ═══════════════════════════════════════════════════════════
#  API — SOCIAL MEDIA PUBLISHING
# ═══════════════════════════════════════════════════════════

@app.route("/api/publish", methods=["POST"])
def api_publish():
    """Publish video to selected platforms."""
    try:
        data = request.get_json()
        video_path = data.get("video_path", "")
        platforms_data = data.get("platforms", {})

        if not video_path or not os.path.exists(video_path):
            return jsonify({"success": False, "error": "Video file not found. Please upload again."})

        if not platforms_data:
            return jsonify({"success": False, "error": "No platforms selected for publishing"})

        result = publish_video(DATABASE_PATH, video_path, platforms_data)

        # Save to history
        save_publish_record(
            video_filename=os.path.basename(video_path),
            platforms=list(platforms_data.keys()),
            results=result.get("results", {}),
            all_success=result.get("all_success", False),
        )

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/platforms")
def api_platforms():
    """Get platform configurations."""
    return jsonify(get_platforms_config())


@app.route("/api/platforms/<platform_key>/fields")
def api_platform_fields(platform_key):
    """Get fields for a specific platform."""
    fields = get_platform_fields(platform_key)
    if not fields:
        return jsonify({"error": "Platform not found"}), 404
    return jsonify(fields)


# ═══════════════════════════════════════════════════════════
#  API — ACCOUNTS
# ═══════════════════════════════════════════════════════════

@app.route("/api/accounts")
def api_accounts():
    """Get all connected accounts."""
    return jsonify(get_accounts(DATABASE_PATH))


@app.route("/api/accounts/connect/<platform>", methods=["POST"])
def api_account_connect(platform):
    """Initiate OAuth connection for a platform."""
    if platform == "youtube":
        if not YOUTUBE_CLIENT_ID:
            # Allow manual token entry
            data = request.get_json()
            access_token = data.get("access_token", "")
            refresh_token = data.get("refresh_token", "")
            account_name = data.get("account_name", "")
            account_id = data.get("account_id", "")
            if access_token:
                save_account(DATABASE_PATH, "youtube", access_token, refresh_token, account_name, account_id)
                return jsonify({"success": True, "message": "YouTube account connected successfully!"})
            return jsonify({"success": False, "error": "No access token provided and no OAuth credentials configured"})

        # OAuth flow
        from google_auth_oauthlib.flow import Flow as GoogleFlow
        client_config = {
            "web": {
                "client_id": YOUTUBE_CLIENT_ID,
                "client_secret": YOUTUBE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [YOUTUBE_REDIRECT_URI],
            }
        }
        flow = GoogleFlow.from_client_config(client_config, scopes=YOUTUBE_SCOPES)
        flow.redirect_uri = YOUTUBE_REDIRECT_URI
        auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
        session["youtube_oauth_state"] = state
        session["youtube_flow"] = client_config
        return jsonify({"success": True, "auth_url": auth_url})

    elif platform == "tiktok":
        if not TIKTOK_CLIENT_KEY:
            data = request.get_json()
            access_token = data.get("access_token", "")
            account_name = data.get("account_name", "")
            if access_token:
                save_account(DATABASE_PATH, "tiktok", access_token, "", account_name, "")
                return jsonify({"success": True, "message": "TikTok account connected successfully!"})
            return jsonify({"success": False, "error": "No access token provided and no OAuth credentials configured"})

        auth_url = (
            f"{TIKTOK_AUTH_URL}?"
            f"client_key={TIKTOK_CLIENT_KEY}&"
            f"scope={','.join(['video.publish'])}&"
            f"response_type=code&"
            f"redirect_uri={TIKTOK_REDIRECT_URI}&"
            f"state=tiktok_auth"
        )
        return jsonify({"success": True, "auth_url": auth_url})

    elif platform in ["instagram", "facebook"]:
        app_id = FACEBOOK_APP_ID
        if not app_id:
            data = request.get_json()
            access_token = data.get("access_token", "")
            account_name = data.get("account_name", "")
            account_id = data.get("account_id", "")
            if access_token:
                save_account(DATABASE_PATH, platform, access_token, "", account_name, account_id)
                return jsonify({"success": True, "message": f"{platform.title()} account connected successfully!"})
            return jsonify({"success": False, "error": "No access token provided and no OAuth credentials configured"})

        scopes = INSTAGRAM_SCOPES if platform == "instagram" else FACEBOOK_SCOPES
        auth_url = (
            f"{FACEBOOK_AUTH_URL}?"
            f"client_id={app_id}&"
            f"redirect_uri={FACEBOOK_REDIRECT_URI}&"
            f"scope={','.join(scopes)}&"
            f"response_type=code&"
            f"state={platform}_auth"
        )
        return jsonify({"success": True, "auth_url": auth_url})

    return jsonify({"success": False, "error": f"Unknown platform: {platform}"})


@app.route("/api/accounts/delete/<platform>", methods=["DELETE"])
def api_account_delete(platform):
    """Delete a connected account."""
    delete_account(DATABASE_PATH, platform)
    return jsonify({"success": True, "message": f"{platform.title()} account disconnected"})


# ═══════════════════════════════════════════════════════════
#  OAUTH CALLBACKS
# ═══════════════════════════════════════════════════════════

@app.route("/auth/youtube/callback")
def auth_youtube_callback():
    """Handle YouTube OAuth callback."""
    try:
        from google_auth_oauthlib.flow import Flow as GoogleFlow
        client_config = session.get("youtube_flow")
        if not client_config:
            return redirect(url_for("accounts_page"))

        flow = GoogleFlow.from_client_config(client_config, scopes=YOUTUBE_SCOPES)
        flow.redirect_uri = YOUTUBE_REDIRECT_URI

        code = request.args.get("code")
        flow.fetch_token(code=code)
        creds = flow.credentials

        save_account(DATABASE_PATH, "youtube", creds.token, creds.refresh_token, "YouTube Account", "")
        return redirect(url_for("accounts_page"))
    except Exception as e:
        return f"YouTube auth failed: {str(e)}", 400


@app.route("/auth/tiktok/callback")
def auth_tiktok_callback():
    """Handle TikTok OAuth callback."""
    try:
        code = request.args.get("code")
        if not code:
            return redirect(url_for("accounts_page"))

        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
        response = requests.post(token_url, data={
            "client_key": TIKTOK_CLIENT_KEY,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": TIKTOK_REDIRECT_URI,
        })
        token_data = response.json()

        if "access_token" in token_data:
            save_account(DATABASE_PATH, "tiktok", token_data["access_token"], "", "TikTok Account", "")
        return redirect(url_for("accounts_page"))
    except Exception as e:
        return f"TikTok auth failed: {str(e)}", 400


@app.route("/auth/facebook/callback")
def auth_facebook_callback():
    """Handle Facebook/Instagram OAuth callback."""
    try:
        code = request.args.get("code")
        state = request.args.get("state", "facebook_auth")
        platform = "facebook" if "facebook" in state else "instagram"

        if not code:
            return redirect(url_for("accounts_page"))

        token_url = f"https://graph.facebook.com/v18.0/oauth/access_token"
        response = requests.get(token_url, params={
            "client_id": FACEBOOK_APP_ID,
            "client_secret": FACEBOOK_APP_SECRET,
            "redirect_uri": FACEBOOK_REDIRECT_URI,
            "code": code,
        })
        token_data = response.json()

        if "access_token" in token_data:
            # Get user/pages info
            me_url = f"https://graph.facebook.com/v18.0/me?access_token={token_data['access_token']}"
            me_response = requests.get(me_url).json()
            account_name = me_response.get("name", f"{platform.title()} Account")
            account_id = me_response.get("id", "")

            save_account(DATABASE_PATH, platform, token_data["access_token"], "", account_name, account_id)
        return redirect(url_for("accounts_page"))
    except Exception as e:
        return f"Facebook auth failed: {str(e)}", 400


# ═══════════════════════════════════════════════════════════
#  API — HISTORY
# ═══════════════════════════════════════════════════════════

@app.route("/api/history/tts")
def api_history_tts():
    """Get TTS history."""
    return jsonify(get_tts_history())


@app.route("/api/history/publish")
def api_history_publish():
    """Get publish history."""
    return jsonify(get_publish_history())


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  Content Publisher — TTS & Video Publishing")
    print("  Running on http://localhost:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
