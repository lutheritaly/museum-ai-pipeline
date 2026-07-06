import os
import sys
from pathlib import Path

# Force load .env from the project root
from dotenv import load_dotenv
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Print debug info
print(f"📂 Current working directory: {os.getcwd()}")
print(f"📄 .env file exists: {Path('.env').exists()}")
print(f"🔑 GOOGLE_SHEETS_ID: {os.environ.get('GOOGLE_SHEETS_ID', 'NOT SET')[:20]}..." if os.environ.get('GOOGLE_SHEETS_ID') else "🔑 GOOGLE_SHEETS_ID: NOT SET")
print(f"🔑 GOOGLE_SHEETS_CREDENTIALS: {'✅ SET' if os.environ.get('GOOGLE_SHEETS_CREDENTIALS') else '❌ NOT SET'}")
print(f"🔑 GROQ_API_KEY: {'✅ SET' if os.environ.get('GROQ_API_KEY') else '❌ NOT SET'}")
print(f"🔑 DEEPGRAM_API_KEY: {'✅ SET' if os.environ.get('DEEPGRAM_API_KEY') else '❌ NOT SET'}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import think, speak

app = FastAPI(
    title="Museum AI Pipeline",
    version="1.0.0",
    description="Split Think+Speak pipeline for museum audio guides"
)

# ✅ ADD THIS SECTION - Serve static files (audio)
static_dir = Path("api/static")
static_dir.mkdir(exist_ok=True)

# Mount the static files directory
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# This makes audio files accessible at /static/audio/filename.mp3

# CORS - allow your museum domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://museo.scattiearte.it",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(think.router, prefix="/api", tags=["Think"])
app.include_router(speak.router, prefix="/api", tags=["Speak"])

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "pipeline": "split",
        "version": "1.0.0",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development")
    }

@app.get("/debug/env")
async def debug_env():
    import os
    return {
        "DEEPGRAM_API_KEY_set": bool(os.environ.get("DEEPGRAM_API_KEY")),
        "GROQ_API_KEY_set": bool(os.environ.get("GROQ_API_KEY")),
        "GOOGLE_SHEETS_ID_set": bool(os.environ.get("GOOGLE_SHEETS_ID")),
        "DEEPGRAM_KEY_LENGTH": len(os.environ.get("DEEPGRAM_API_KEY", "")),
        "all_keys": list(os.environ.keys())
    }

# 🚀 Startup event - runs when the server starts
@app.on_event("startup")
async def startup_event():
    print("🚀 Server starting up...")
    # Force cache load on startup
    from api.services.google_sheets import get_artifact_context
    test_context = get_artifact_context("101")
    if test_context:
        print(f"✅ Cache loaded successfully! Found artifact: {test_context.get('name')}")
    else:
        print("⚠️ No artifacts loaded yet")