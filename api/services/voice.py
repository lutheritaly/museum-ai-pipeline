import os
import requests
import uuid
from pathlib import Path

DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# Use absolute path for audio storage
PROJECT_ROOT = Path(__file__).parent.parent.parent
AUDIO_DIR = PROJECT_ROOT / "api" / "static" / "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def synthesize_speech(text: str, language: str, voice_id: str) -> str:
    """Generate speech and return a URL to the audio file"""
    
    if not DEEPGRAM_API_KEY:
        raise Exception("DEEPGRAM_API_KEY not set")
    
    print(f"🎤 Generating speech for: {text[:50]}...")
    
    try:
        if voice_id.startswith("aura-") or "deepgram" in voice_id:
            return _deepgram_aura_with_file(text, voice_id)
        elif voice_id.startswith("eleven_"):
            return _elevenlabs_with_file(text, voice_id)
        else:
            return _deepgram_aura_with_file(text, "aura-2-thalia-it")
    except Exception as e:
        print(f"❌ Voice error: {e}")
        raise

def _deepgram_aura_with_file(text: str, voice_id: str) -> str:
    """Generate speech using Deepgram Aura TTS and save to a file"""
    
    url = f"https://api.deepgram.com/v1/speak?model={voice_id}"
    
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Save to a file with .mp3 extension
        audio_id = str(uuid.uuid4())
        audio_path = AUDIO_DIR / f"{audio_id}.mp3"
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        
        print(f"📀 Audio saved: {audio_path} ({len(response.content)} bytes)")
        
        # ✅ Return URL with static path
        return f"/static/audio/{audio_id}.mp3"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Deepgram API Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"📝 Response: {e.response.text}")
        raise

def _elevenlabs_with_file(text: str, voice_id: str) -> str:
    """Generate speech using ElevenLabs and save to a file"""
    if not ELEVENLABS_API_KEY:
        raise Exception("ELEVENLABS_API_KEY not set")
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    
    audio_id = str(uuid.uuid4())
    audio_path = AUDIO_DIR / f"{audio_id}.mp3"
    with open(audio_path, 'wb') as f:
        f.write(response.content)
    
    # ✅ Return URL with static path
    return f"/static/audio/{audio_id}.mp3"