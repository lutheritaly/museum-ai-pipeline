from fastapi import APIRouter, HTTPException
from api.models.schemas import ThinkRequest, ThinkResponse
from api.services.google_sheets import get_artifact_context
from api.services.brain import BrainRouter
from api.services.cache import cache_tts
import uuid
import time

router = APIRouter()

@router.post("/think", response_model=ThinkResponse)
async def think_step(request: ThinkRequest):
    """Step 1: Generate AI response (fast, under 10s)"""
    start_time = time.time()
    
    context = get_artifact_context(request.artifact_id)
    if not context:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Use opening monologue if no user input
    if not request.user_input:
        user_input = context.get("opening_monologue", {}).get(request.language, "")
        if user_input:
            return ThinkResponse(
                session_id=str(uuid.uuid4()),
                text=user_input,
                language=request.language,
                artifact_name=context["name"],
                tts_cache_key=cache_tts.generate_key(
                    request.artifact_id, 
                    request.language, 
                    user_input
                )
            )
    
    response_text = BrainRouter.generate(
        context=context,
        user_input=request.user_input,
        language=request.language,
        provider=context.get("backup_brain", "groq"),
        model=context.get("backup_brain_model", "llama3-8b-8192")
    )
    
    session_id = str(uuid.uuid4())
    cache_key = cache_tts.generate_key(request.artifact_id, request.language, response_text)
    cache_tts.set(cache_key, response_text)
    
    elapsed = time.time() - start_time
    print(f"✅ Think step: {elapsed:.2f}s")
    
    return ThinkResponse(
        session_id=session_id,
        text=response_text,
        language=request.language,
        artifact_name=context["name"],
        tts_cache_key=cache_key
    )