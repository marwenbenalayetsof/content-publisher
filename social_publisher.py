"""
Social Media Publisher Module
Handles publishing to YouTube, TikTok, Instagram, and Facebook
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ═══════════════════════════════════════════════════════════
#  PLATFORM CONFIGURATION
# ═══════════════════════════════════════════════════════════

PLATFORMS = {
    "youtube": {
        "name": "YouTube",
        "icon": "play-circle",
        "color": "#FF0000",
        "fields": [
            {"key": "title", "label": "Video Title", "type": "text", "required": True, "max_length": 100},
            {"key": "description", "label": "Description", "type": "textarea", "required": False, "max_length": 5000},
            {"key": "tags", "label": "Tags (comma separated)", "type": "text", "required": False},
            {"key": "category", "label": "Category", "type": "select", "required": True,
             "options": [
                 {"value": "22", "label": "People & Blogs"},
                 {"value": "24", "label": "Entertainment"},
                 {"value": "28", "label": "Science & Technology"},
                 {"value": "27", "label": "Education"},
                 {"value": "20", "label": "Gaming"},
                 {"value": "17", "label": "Sports"},
                 {"value": "19", "label": "Travel & Events"},
                 {"value": "2", "label": "Autos & Vehicles"},
                 {"value": "10", "label": "Music"},
                 {"value": "26", "label": "How-to & Style"},
                 {"value": "25", "label": "News & Politics"},
                 {"value": "29", "label": "Nonprofits & Activism"},
             ]},
            {"key": "privacy", "label": "Privacy", "type": "select", "required": True,
             "options": [
                 {"value": "public", "label": "Public"},
                 {"value": "unlisted", "label": "Unlisted"},
                 {"value": "private", "label": "Private"},
             ]},
            {"key": "made_for_kids", "label": "Made for Kids", "type": "checkbox", "required": True},
            {"key": "embeddable", "label": "Allow Embedding", "type": "checkbox", "required": False},
            {"key": "notify_subscribers", "label": "Notify Subscribers", "type": "checkbox", "required": False},
        ],
        "auth_type": "oauth2",
    },
    "tiktok": {
        "name": "TikTok",
        "icon": "music",
        "color": "#000000",
        "fields": [
            {"key": "title", "label": "Video Title", "type": "text", "required": True, "max_length": 150},
            {"key": "privacy", "label": "Privacy", "type": "select", "required": True,
             "options": [
                 {"value": "PUBLIC_TO_EVERYONE", "label": "Public"},
                 {"value": "MUTUAL_FOLLOW_FRIENDS", "label": "Friends Only"},
                 {"value": "FOLLOWER_OF_CREATOR", "label": "Followers Only"},
                 {"value": "SELF_ONLY", "label": "Private"},
             ]},
            {"key": "allow_comments", "label": "Allow Comments", "type": "checkbox", "required": False},
            {"key": "allow_duet", "label": "Allow Duet", "type": "checkbox", "required": False},
            {"key": "allow_stitch", "label": "Allow Stitch", "type": "checkbox", "required": False},
            {"key": "disable_comment", "label": "Disable Commercial Content", "type": "checkbox", "required": False},
        ],
        "auth_type": "oauth2",
    },
    "instagram": {
        "name": "Instagram",
        "icon": "camera",
        "color": "#E4405F",
        "fields": [
            {"key": "caption", "label": "Caption", "type": "textarea", "required": False, "max_length": 2200},
            {"key": "share_to_feed", "label": "Share to Feed (Reel)", "type": "checkbox", "required": False},
            {"key": "share_to_story", "label": "Share to Story", "type": "checkbox", "required": False},
        ],
        "auth_type": "oauth2",
    },
    "facebook": {
        "name": "Facebook",
        "icon": "facebook",
        "color": "#1877F2",
        "fields": [
            {"key": "title", "label": "Video Title", "type": "text", "required": True, "max_length": 255},
            {"key": "description", "label": "Description", "type": "textarea", "required": False, "max_length": 5000},
            {"key": "tags", "label": "Tags (comma separated)", "type": "text", "required": False},
            {"key": "privacy", "label": "Privacy", "type": "select", "required": True,
             "options": [
                 {"value": "PUBLIC", "label": "Public"},
                 {"value": "FRIENDS", "label": "Friends"},
                 {"value": "ONLY_ME", "label": "Only Me"},
             ]},
            {"key": "allow_hd", "label": "Allow HD Upload", "type": "checkbox", "required": False},
        ],
        "auth_type": "oauth2",
    },
}


def get_platforms_config():
    """Return platforms configuration for the frontend."""
    return PLATFORMS


def get_platform_fields(platform_key: str) -> list:
    """Get the fields for a specific platform."""
    platform = PLATFORMS.get(platform_key, {})
    return platform.get("fields", [])


# ═══════════════════════════════════════════════════════════
#  DATABASE HELPERS FOR ACCOUNTS
# ═══════════════════════════════════════════════════════════

def get_db_connection(db_path: str):
    """Get a database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_accounts(db_path: str) -> list:
    """Get all connected accounts."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM social_accounts ORDER BY platform")
    accounts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return accounts


def get_account_by_platform(db_path: str, platform: str) -> dict:
    """Get account for a specific platform."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM social_accounts WHERE platform = ?", (platform,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_account(db_path: str, platform: str, access_token: str,
                 refresh_token: str = None, account_name: str = "",
                 account_id: str = "") -> bool:
    """Save or update a social media account."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO social_accounts (platform, access_token, refresh_token, account_name, account_id, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(platform) DO UPDATE SET
            access_token = excluded.access_token,
            refresh_token = excluded.refresh_token,
            account_name = excluded.account_name,
            account_id = excluded.account_id,
            updated_at = excluded.updated_at
    """, (platform, access_token, refresh_token, account_name, account_id,
          datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True


def delete_account(db_path: str, platform: str) -> bool:
    """Delete a social media account."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM social_accounts WHERE platform = ?", (platform,))
    conn.commit()
    conn.close()
    return True


# ═══════════════════════════════════════════════════════════
#  YOUTUBE PUBLISHING
# ═══════════════════════════════════════════════════════════

def publish_to_youtube(db_path: str, video_path: str, metadata: dict,
                       client_secrets_file: str = None) -> dict:
    """Publish a video to YouTube."""
    try:
        account = get_account_by_platform(db_path, "youtube")
        if not account or not account.get("access_token"):
            return {"success": False, "error": "YouTube account not connected. Please connect your account first."}

        creds = Credentials(token=account["access_token"],
                           refresh_token=account.get("refresh_token"),
                           token_uri="https://oauth2.googleapis.com/token",
                           client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
                           client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""))

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "tags": [t.strip() for t in metadata.get("tags", "").split(",") if t.strip()],
                "categoryId": metadata.get("category", "22"),
            },
            "status": {
                "privacyStatus": metadata.get("privacy", "private"),
                "selfDeclaredMadeForKids": metadata.get("made_for_kids", False),
                "embeddable": metadata.get("embeddable", True),
                "notifySubscribers": metadata.get("notify_subscribers", True),
            },
        }

        media = MediaFileUpload(video_path, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )
        response = request.execute()

        return {
            "success": True,
            "video_id": response.get("id"),
            "video_url": f"https://www.youtube.com/watch?v={response.get('id')}",
            "platform": "youtube",
            "message": "Video published successfully to YouTube!",
        }
    except Exception as e:
        return {"success": False, "error": f"YouTube publishing failed: {str(e)}"}


# ═══════════════════════════════════════════════════════════
#  TIKTOK PUBLISHING
# ═══════════════════════════════════════════════════════════

def publish_to_tiktok(db_path: str, video_path: str, metadata: dict) -> dict:
    """Publish a video to TikTok via Content Posting API."""
    try:
        account = get_account_by_platform(db_path, "tiktok")
        if not account or not account.get("access_token"):
            return {"success": False, "error": "TikTok account not connected. Please connect your account first."}

        access_token = account["access_token"]

        # Step 1: Initialize upload
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        init_body = {
            "post_info": {
                "title": metadata.get("title", ""),
                "privacy_level": metadata.get("privacy", "PUBLIC_TO_EVERYONE"),
                "disable_duet": not metadata.get("allow_duet", True),
                "disable_comment": not metadata.get("allow_comments", True),
                "disable_stitch": not metadata.get("allow_stitch", True),
                "video_cover_timestamp_ms": 1000,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": "",
            },
        }

        # For direct upload, we need to use chunked upload
        # First, get video file size
        video_size = os.path.getsize(video_path)

        init_body_direct = {
            "post_info": init_body["post_info"],
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": video_size,
                "total_chunk_count": 1,
            },
        }

        init_response = requests.post(init_url, headers=headers, json=init_body_direct)
        init_data = init_response.json()

        if init_data.get("error", {}).get("code") != "ok":
            return {"success": False, "error": f"TikTok init failed: {init_data.get('error', {}).get('message', 'Unknown error')}"}

        publish_id = init_data["data"]["publish_id"]
        upload_url = init_data["data"]["upload_url"]

        # Step 2: Upload video chunk
        with open(video_path, "rb") as f:
            video_data = f.read()

        upload_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
        }
        upload_response = requests.put(upload_url, headers=upload_headers, data=video_data)

        if upload_response.status_code not in [200, 201]:
            return {"success": False, "error": f"TikTok upload failed: {upload_response.text}"}

        return {
            "success": True,
            "publish_id": publish_id,
            "platform": "tiktok",
            "message": "Video published successfully to TikTok!",
        }
    except Exception as e:
        return {"success": False, "error": f"TikTok publishing failed: {str(e)}"}


# ═══════════════════════════════════════════════════════════
#  INSTAGRAM PUBLISHING
# ═══════════════════════════════════════════════════════════

def publish_to_instagram(db_path: str, video_path: str, metadata: dict) -> dict:
    """Publish a video to Instagram via Graph API (Reels)."""
    try:
        account = get_account_by_platform(db_path, "instagram")
        if not account or not account.get("access_token"):
            return {"success": False, "error": "Instagram account not connected. Please connect your account first."}

        access_token = account["access_token"]
        ig_user_id = account.get("account_id", "")

        if not ig_user_id:
            return {"success": False, "error": "Instagram Business Account ID not found. Please reconnect."}

        # Step 1: Create media container
        create_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
        create_data = {
            "media_type": "REELS",
            "caption": metadata.get("caption", ""),
            "access_token": access_token,
        }

        # Upload video from file
        # Instagram Graph API requires a URL or file upload
        # For local files, we need to use the resumable upload approach
        create_data["upload_type"] = "multipart"

        create_response = requests.post(create_url, data=create_data)
        create_result = create_response.json()

        if "id" not in create_result:
            return {"success": False, "error": f"Instagram container creation failed: {create_result}"}

        container_id = create_result["id"]

        # Step 2: Upload video binary
        video_size = os.path.getsize(video_path)
        upload_url = f"https://rupload.facebook.com/video-upload/v18.0/{container_id}"
        upload_headers = {
            "Authorization": f"OAuth {access_token}",
            "offset": "0",
            "file_size": str(video_size),
        }

        with open(video_path, "rb") as f:
            video_data = f.read()

        upload_response = requests.post(upload_url, headers=upload_headers, data=video_data)

        # Step 3: Publish the container
        import time
        # Wait for processing
        for _ in range(30):
            check_url = f"https://graph.facebook.com/v18.0/{container_id}?fields=status_code&access_token={access_token}"
            check_response = requests.get(check_url).json()
            status = check_response.get("status_code")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                return {"success": False, "error": "Instagram video processing failed"}
            time.sleep(5)

        publish_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
        publish_data = {
            "creation_id": container_id,
            "access_token": access_token,
        }
        publish_response = requests.post(publish_url, data=publish_data)
        publish_result = publish_response.json()

        if "id" not in publish_result:
            return {"success": False, "error": f"Instagram publishing failed: {publish_result}"}

        return {
            "success": True,
            "media_id": publish_result["id"],
            "platform": "instagram",
            "message": "Video published successfully to Instagram!",
        }
    except Exception as e:
        return {"success": False, "error": f"Instagram publishing failed: {str(e)}"}


# ═══════════════════════════════════════════════════════════
#  FACEBOOK PUBLISHING
# ═══════════════════════════════════════════════════════════

def publish_to_facebook(db_path: str, video_path: str, metadata: dict) -> dict:
    """Publish a video to Facebook Page."""
    try:
        account = get_account_by_platform(db_path, "facebook")
        if not account or not account.get("access_token"):
            return {"success": False, "error": "Facebook account not connected. Please connect your account first."}

        access_token = account["access_token"]
        page_id = account.get("account_id", "")

        if not page_id:
            return {"success": False, "error": "Facebook Page ID not found. Please reconnect."}

        # Upload video to Facebook Page
        url = f"https://graph.facebook.com/v18.0/{page_id}/videos"

        with open(video_path, "rb") as f:
            files = {"file": f}
            data = {
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "access_token": access_token,
            }

            if metadata.get("tags"):
                data["tags"] = metadata.get("tags")

            response = requests.post(url, files=files, data=data)

        result = response.json()

        if "id" not in result:
            return {"success": False, "error": f"Facebook publishing failed: {result}"}

        return {
            "success": True,
            "video_id": result["id"],
            "platform": "facebook",
            "message": "Video published successfully to Facebook!",
        }
    except Exception as e:
        return {"success": False, "error": f"Facebook publishing failed: {str(e)}"}


# ═══════════════════════════════════════════════════════════
#  UNIFIED PUBLISH FUNCTION
# ═══════════════════════════════════════════════════════════

def publish_video(db_path: str, video_path: str, platforms_data: dict) -> dict:
    """
    Publish video to multiple platforms.
    platforms_data: {"youtube": {...metadata}, "tiktok": {...}, ...}
    """
    results = {}

    publishers = {
        "youtube": publish_to_youtube,
        "tiktok": publish_to_tiktok,
        "instagram": publish_to_instagram,
        "facebook": publish_to_facebook,
    }

    for platform_key, metadata in platforms_data.items():
        if platform_key in publishers:
            results[platform_key] = publishers[platform_key](db_path, video_path, metadata)
        else:
            results[platform_key] = {"success": False, "error": f"Unknown platform: {platform_key}"}

    all_success = all(r.get("success", False) for r in results.values())
    any_success = any(r.get("success", False) for r in results.values())

    return {
        "results": results,
        "all_success": all_success,
        "any_success": any_success,
        "summary": _generate_summary(results),
    }


def _generate_summary(results: dict) -> str:
    """Generate a human-readable summary of publishing results."""
    lines = []
    for platform, result in results.items():
        status = "SUCCESS" if result.get("success") else "FAILED"
        emoji = "ok" if result.get("success") else "error"
        error_msg = f" — {result.get('error', '')}" if not result.get("success") else ""
        lines.append(f"[{emoji}] {platform.upper()}: {status}{error_msg}")
    return "\n".join(lines)
