# Content Publisher

Professional TTS Voice Generator & Social Media Video Publisher.

## Features

### Voice Studio
- **12 Professional AI Voices** — National Geographic, BBC, Australian, and more narration styles
- **6 Narration Presets** — Documentary, History Channel, Dramatic, Calm, News, Energetic
- **Smart Text Preprocessing** — Automatically expands abbreviations (US → United States, WWII → World War Two)
- **Auto-chunking** — Handles long scripts by splitting at sentence boundaries
- **Auto-download** — MP3 is automatically downloaded with your chosen filename

### Video Publisher
- **Multi-platform publishing** — YouTube, TikTok, Instagram, Facebook
- **Platform-specific fields** — Each platform has tailored metadata options:
  - YouTube: Title, Description, Tags, Category, Privacy, Made for Kids
  - TikTok: Title, Privacy, Allow Comments/Duet/Stitch
  - Instagram: Caption, Share to Feed/Story
  - Facebook: Title, Description, Tags, Privacy
- **Account Management** — Connect, update, and disconnect social media accounts
- **Publishing History** — Track all your publications with success/failure status

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/content-publisher.git
cd content-publisher

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) Install ffmpeg for long script merging
# On Windows: Download from https://ffmpeg.org/download.html
# On macOS: brew install ffmpeg
# On Ubuntu: sudo apt install ffmpeg

# 6. (Optional) Configure social media OAuth
cp .env.example .env
# Edit .env with your API credentials

# 7. Run the application
python app.py

# 8. Open in browser
# http://localhost:5000
```

## Project Structure

```
content-publisher/
├── app.py                  # Main Flask application
├── config.py               # Configuration & environment variables
├── models.py               # SQLite database models
├── tts_engine.py           # TTS engine (edge-tts based)
├── social_publisher.py     # Social media publishing module
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── static/
│   ├── css/
│   │   └── style.css       # Modern dark UI theme
│   └── js/
│       └── app.js          # Client-side JavaScript
├── templates/
│   ├── base.html           # Base template with sidebar
│   ├── index.html          # Voice Studio page
│   ├── publish.html        # Video Publisher page
│   └── accounts.html       # Account Management page
├── data/                   # SQLite database (auto-created)
├── output/                 # Generated MP3 files
└── uploads/                # Uploaded video files
```

## Social Media Setup

### YouTube
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Set `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` in `.env`

### TikTok
1. Go to [TikTok Developer Portal](https://developers.tiktok.com/)
2. Create an app and request Content Posting API access
3. Set `TIKTOK_CLIENT_KEY` and `TIKTOK_CLIENT_SECRET` in `.env`

### Instagram / Facebook
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create an app with Instagram Graph API and Facebook Login
3. Set `FACEBOOK_APP_ID` and `FACEBOOK_APP_SECRET` in `.env`

### Manual Token Connection
If you don't have OAuth credentials configured, you can connect accounts by pasting access tokens directly in the Accounts page or the publish form.

## Technology Stack

- **Backend**: Python 3.10+, Flask
- **TTS**: edge-tts (Microsoft Azure Neural Voices)
- **Database**: SQLite
- **Frontend**: Vanilla HTML/CSS/JS with dark theme
- **Social APIs**: YouTube Data API v3, TikTok Content Posting API, Meta Graph API

## License

MIT
