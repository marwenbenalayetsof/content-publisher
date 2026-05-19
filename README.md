# Content Publisher

**Two-in-one tool**: Generate voice MP3 from your script + Upload & publish videos to social media.

## Features

### Voice Studio
- Paste your English script → Choose a voice → Get MP3
- **12 Professional AI Voices** — Christopher (NatGeo), Guy, Ryan (BBC), Thomas, William, Eric, Davis, Tony, Sonia, Ava, Mia, Natasha
- **6 Narration Styles** — Documentary, History Channel, Dramatic, Calm, News, Energetic
- Auto-download MP3 with your chosen filename
- Audio preview player
- History of all generations

### Video Publisher
- Upload a video from your computer
- Choose platforms: YouTube, TikTok, Instagram, Facebook
- Fill in platform-specific details (title, description, tags, privacy, etc.)
- Connect your social media accounts (saved for future use)
- Publish to multiple platforms at once
- Get success/failure notifications

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/marwenbenalayetsof/content-publisher.git
cd content-publisher

# 2. Create virtual environment
python -m venv venv

# 3. Activate
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) Install ffmpeg for long script merging
# Windows: Download from https://ffmpeg.org
# Mac: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg

# 6. Run
python app.py

# 7. Open browser
# http://localhost:5000
```

## Project Structure

```
content-publisher/
├── app.py                  # Flask application
├── config.py               # Configuration
├── models.py               # SQLite database
├── tts_engine.py           # TTS voice generation
├── social_publisher.py     # Social media publishing
├── requirements.txt
├── .env.example
├── static/css/style.css    # Dark UI theme
├── static/js/app.js
├── templates/
│   ├── base.html           # Layout with sidebar
│   ├── index.html          # Voice Studio
│   ├── publish.html        # Video Publisher
│   └── accounts.html       # Account Management
├── data/                   # SQLite DB (auto-created)
├── output/                 # Generated MP3 files
└── uploads/                # Uploaded video files
```

## Social Media Setup

Set credentials in `.env` file (copy `.env.example`):

- **YouTube**: `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` from [Google Cloud Console](https://console.cloud.google.com/)
- **TikTok**: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` from [TikTok Developer Portal](https://developers.tiktok.com/)
- **Facebook/Instagram**: `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET` from [Meta for Developers](https://developers.facebook.com/)

You can also connect accounts by pasting access tokens directly in the UI.

## Tech Stack

- Python 3.12 + Flask
- edge-tts (Microsoft Azure Neural Voices)
- SQLite
- Vanilla HTML/CSS/JS dark theme

## License

MIT
