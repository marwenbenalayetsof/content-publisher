"""
TTS Engine — Voice Generation from Script
Based on edge-tts with 12 professional narration voices
"""

import asyncio
import edge_tts
import re
import os
import subprocess
from datetime import datetime


# ═══════════════════════════════════════════════════════════
#  VOICE CONFIGURATION — 12 Professional Narration Voices
# ═══════════════════════════════════════════════════════════

VOICES = {
    "1": {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher",
        "flag": "US",
        "description": "Deep, authoritative — National Geographic style",
        "gender": "Male",
        "recommended": True,
    },
    "2": {
        "id": "en-US-GuyNeural",
        "name": "Guy",
        "flag": "US",
        "description": "Warm, strong narrator — Classic documentary",
        "gender": "Male",
    },
    "3": {
        "id": "en-GB-RyanNeural",
        "name": "Ryan",
        "flag": "GB",
        "description": "BBC-style British documentary narrator",
        "gender": "Male",
    },
    "4": {
        "id": "en-GB-ThomasNeural",
        "name": "Thomas",
        "flag": "GB",
        "description": "Classic British narrator — David Attenborough feel",
        "gender": "Male",
    },
    "5": {
        "id": "en-AU-WilliamNeural",
        "name": "William",
        "flag": "AU",
        "description": "Australian documentary — Outback stories",
        "gender": "Male",
    },
    "6": {
        "id": "en-US-EricNeural",
        "name": "Eric",
        "flag": "US",
        "description": "Deep American narrator — Cinematic & dramatic",
        "gender": "Male",
    },
    "7": {
        "id": "en-US-DavisNeural",
        "name": "Davis",
        "flag": "US",
        "description": "Gravelly, intense narrator — True crime & thriller",
        "gender": "Male",
    },
    "8": {
        "id": "en-US-TonyNeural",
        "name": "Tony",
        "flag": "US",
        "description": "Smooth, professional — Corporate & tech narration",
        "gender": "Male",
    },
    "9": {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia",
        "flag": "GB",
        "description": "British female narrator — Elegant & refined",
        "gender": "Female",
    },
    "10": {
        "id": "en-US-AvaNeural",
        "name": "Ava",
        "flag": "US",
        "description": "American female narrator — Warm & engaging",
        "gender": "Female",
    },
    "11": {
        "id": "en-GB-MiaNeural",
        "name": "Mia",
        "flag": "GB",
        "description": "Soft British female — Nature & wildlife narration",
        "gender": "Female",
    },
    "12": {
        "id": "en-AU-NatashaNeural",
        "name": "Natasha",
        "flag": "AU",
        "description": "Australian female — Travel & adventure narration",
        "gender": "Female",
    },
}

# Narration style presets (rate = speed, pitch = depth)
PRESETS = {
    "documentary": {
        "rate": "-8%",
        "pitch": "-4Hz",
        "label": "Documentary / National Geographic",
        "icon": "film",
    },
    "history": {
        "rate": "-12%",
        "pitch": "-6Hz",
        "label": "History Channel — slower, heavier",
        "icon": "scroll",
    },
    "news": {
        "rate": "+0%",
        "pitch": "+0Hz",
        "label": "News / Neutral narration",
        "icon": "newspaper",
    },
    "dramatic": {
        "rate": "-5%",
        "pitch": "-8Hz",
        "label": "Dramatic / Cinematic — intense & deep",
        "icon": "clapperboard",
    },
    "calm": {
        "rate": "-15%",
        "pitch": "-2Hz",
        "label": "Calm / Meditation — slow & peaceful",
        "icon": "cloud",
    },
    "energetic": {
        "rate": "+5%",
        "pitch": "+2Hz",
        "label": "Energetic / YouTube — upbeat & fast",
        "icon": "zap",
    },
}


# ═══════════════════════════════════════════════════════════
#  TEXT SPLITTING (for long scripts)
# ═══════════════════════════════════════════════════════════

def split_into_chunks(text: str, max_chars: int = 4500) -> list:
    """Split long text into sentence-boundary chunks."""
    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current += (" " if current else "") + sentence
        else:
            if current:
                chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks


# ═══════════════════════════════════════════════════════════
#  VOICE GENERATION
# ═══════════════════════════════════════════════════════════

async def generate_chunk(text: str, voice: str, rate: str,
                         pitch: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)


async def generate_audio(text: str, voice: str, rate: str,
                         pitch: str, output_file: str):
    """Generate TTS audio, auto-splitting long texts into chunks."""
    chunks = split_into_chunks(text)

    if len(chunks) == 1:
        await generate_chunk(text, voice, rate, pitch, output_file)
        return

    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_path = output_file.replace(".mp3", f"_chunk{i:03d}.mp3")
        await generate_chunk(chunk, voice, rate, pitch, chunk_path)
        chunk_files.append(chunk_path)

    try:
        list_file = output_file.replace(".mp3", "_concat.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for cf in chunk_files:
                f.write(f"file '{os.path.abspath(cf)}'\n")

        result = subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', list_file, '-c', 'copy', output_file,
            '-y', '-loglevel', 'quiet'
        ], timeout=300)

        if result.returncode == 0:
            for cf in chunk_files:
                os.remove(cf)
            os.remove(list_file)
        else:
            print(f"Warning: ffmpeg merge failed — keeping {len(chunks)} parts.")

    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("Warning: ffmpeg not found — keeping chunk files.")


def generate_tts(prompt: str, voice_key: str, preset_key: str,
                 filename: str, output_dir: str = "output") -> dict:
    """
    Generate MP3 from script text.
    Returns dict with success status, file path, and metadata.
    """
    voice_info = VOICES.get(voice_key, VOICES["1"])
    preset_info = PRESETS.get(preset_key, PRESETS["documentary"])

    voice_id = voice_info["id"]
    rate = preset_info["rate"]
    pitch = preset_info["pitch"]

    if not prompt.strip():
        return {"success": False, "error": "Please enter your script text"}

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    if not filename.strip():
        filename = f"narration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Clean filename
    filename = re.sub(r'[^\w\s-]', '', filename).strip()
    filename = re.sub(r'[-\s]+', '_', filename)

    output_file = os.path.join(output_dir, f"{filename}.mp3")

    # Generate audio directly from prompt — no preprocessing
    try:
        asyncio.run(
            generate_audio(prompt.strip(), voice_id, rate, pitch, output_file)
        )
    except Exception as e:
        return {"success": False, "error": str(e)}

    if os.path.exists(output_file):
        size_kb = os.path.getsize(output_file) / 1024
        return {
            "success": True,
            "file_path": output_file,
            "filename": f"{filename}.mp3",
            "size_kb": round(size_kb, 1),
            "voice": voice_info["name"],
            "preset": preset_info["label"],
        }
    else:
        return {"success": False, "error": "Audio file was not created"}
