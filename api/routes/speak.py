from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from api.services.voice import synthesize_speech
from api.services.cache import cache_tts
from api.services.google_sheets import get_artifact_context
import time

router = APIRouter()

@router.get("/speak")
async def speak_step(
    text: str = Query(..., description="Text to synthesize"),
    language: str = Query("it", description="Language code"),
    artifact_id: str = Query(..., description="Artifact ID to get voice from sheet"),
    cache_key: str = Query(None, description="Cache key for pre-generated text")
):
    """Step 2: Generate TTS audio using voice from Google Sheets"""
    start_time = time.time()
    
    # Get voice ID from Google Sheets
    context = get_artifact_context(artifact_id)
    if not context:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    voice_id = context.get("backup_voice_id", "aura-2-thalia-it")
    print(f"🎤 Using voice from sheet: {voice_id}")
    
    # Check cache first
    if cache_key:
        cached_url = cache_tts.get_audio_url(cache_key)
        if cached_url:
            return JSONResponse({
                "audio_url": cached_url,
                "cached": True,
                "generation_time_ms": 0,
                "voice_id": voice_id
            })
    
    # Truncate to prevent abuse
    if len(text) > 500:
        text = text[:500] + "..."
    
    try:
        audio_url = synthesize_speech(
            text=text,
            language=language,
            voice_id=voice_id
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        if cache_key:
            cache_tts.store_audio_url(cache_key, audio_url)
        
        return JSONResponse({
            "audio_url": audio_url,
            "cached": False,
            "generation_time_ms": round(elapsed, 2),
            "voice_id": voice_id
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"TTS generation failed: {str(e)}"
        )