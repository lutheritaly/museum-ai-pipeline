from pydantic import BaseModel
from typing import Optional

class ThinkRequest(BaseModel):
    artifact_id: str
    user_input: Optional[str] = None
    language: str = "it"

class ThinkResponse(BaseModel):
    session_id: str
    text: str
    language: str
    artifact_name: str
    tts_cache_key: str

class SpeakRequest(BaseModel):
    text: str
    language: str = "it"
    voice_id: str = "aura-2-thalia-it"
    cache_key: Optional[str] = None

class SpeakResponse(BaseModel):
    audio_url: str
    cached: bool
    generation_time_ms: float
    voice_id: str