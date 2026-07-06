import os
import time
import json
import requests
from typing import Optional, Dict
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load credentials from environment
GOOGLE_SHEETS_CREDENTIALS = json.loads(os.environ.get("GOOGLE_SHEETS_CREDENTIALS", "{}"))
SHEET_ID = os.environ.get("GOOGLE_SHEETS_ID", "")

class SheetCache:
    _cache: Dict[str, Dict] = {}
    _last_fetch = 0
    _cache_ttl = 60  # Refresh every minute
    _initialized = False
    
    @classmethod
    def _ensure_initialized(cls):
        """Ensure the cache is loaded at least once"""
        if not cls._initialized:
            print("🔄 Initializing cache for the first time...")
            cls._refresh_cache()
            cls._initialized = True
    
    @classmethod
    def get_context(cls, artifact_id: str) -> Optional[Dict]:
        cls._ensure_initialized()  # This ensures cache is loaded
        current_time = time.time()
        if current_time - cls._last_fetch > cls._cache_ttl:
            cls._refresh_cache()
        
        return cls._cache.get(artifact_id)
    
    @classmethod
    def _refresh_cache(cls):
        print("🔄 Refreshing cache...")
        
        if not GOOGLE_SHEETS_CREDENTIALS or not SHEET_ID:
            print("❌ Missing Google Sheets credentials or Sheet ID")
            print(f"  - Credentials present: {bool(GOOGLE_SHEETS_CREDENTIALS)}")
            print(f"  - Sheet ID present: {bool(SHEET_ID)}")
            # Add test artifact if credentials missing
            cls._add_test_artifact()
            return
        
        try:
            print("🔄 Attempting to connect to Google Sheets...")
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                GOOGLE_SHEETS_CREDENTIALS, scope
            )
            client = gspread.authorize(creds)
            print(f"✅ Connected to Google Sheets API")
            
            sheet = client.open_by_key(SHEET_ID).sheet1
            print(f"✅ Opened sheet: {sheet.title}")
            
            records = sheet.get_all_records()
            print(f"📊 Found {len(records)} rows in the sheet")
            
            # Clear existing cache
            cls._cache = {}
            
            # Print the first row to see column names
            if records:
                print(f"📋 Column headers: {list(records[0].keys())}")
            
            for row in records:
                artifact_id = str(row.get("Artifact ID", "")).strip()
                if not artifact_id:
                    continue
                
                doc_url = row.get("Google Doc Link", "")
                context_text = cls._extract_google_doc_content(doc_url) if doc_url else ""
                
                cls._cache[artifact_id] = {
                    "id": artifact_id,
                    "name": row.get("Artifact Name", "Unknown Artifact"),
                    "hall": row.get("Hall Name", ""),
                    "context_text": context_text,
                    "opening_monologue": {
                        "it": row.get("Opening IT", ""),
                        "en": row.get("Opening EN", ""),
                        "es": row.get("Opening ES", ""),
                        "fr": row.get("Opening FR", "")
                    },
                    "status": row.get("Status", "active"),
                    "backup_brain": row.get("Backup Brain Platform", "groq"),
                    "backup_brain_model": row.get("Backup Brain Model", "llama3-8b-8192"),
                    "backup_voice": row.get("Backup Voice Platform", "deepgram"),
                    "backup_voice_id": row.get("Backup Voice ID", "aura-2-thalia-it"),
                    "nfc_url": row.get("NFC URL Destination", ""),
                    "code": str(row.get("3-Digit Code", ""))
                }
            
            cls._last_fetch = time.time()
            print(f"✅ Loaded {len(cls._cache)} artifacts from Google Sheets")
            
            # If no artifacts found, add test artifact
            if not cls._cache:
                cls._add_test_artifact()
            
        except Exception as e:
            print(f"❌ Error fetching from Google Sheets: {e}")
            import traceback
            traceback.print_exc()
            # Add test artifact on error
            cls._add_test_artifact()
    
    @classmethod
    def _add_test_artifact(cls):
        """Add a test artifact so the API works even without Google Sheets"""
        if "101" not in cls._cache:
            print("⚠️ Adding test artifact (Google Sheets connection failed or empty)")
            cls._cache["101"] = {
                "id": "101",
                "name": "Test Artifact (Fallback)",
                "hall": "Test Hall",
                "context_text": "This is a test artifact for the museum AI pipeline.",
                "opening_monologue": {
                    "it": "Benvenuti al Museo. Questa è un'opera d'arte di test.",
                    "en": "Welcome to the museum. This is a test artwork.",
                    "es": "Bienvenidos al museo. Esta es una obra de arte de prueba.",
                    "fr": "Bienvenue au musée. Ceci est une œuvre d'art de test."
                },
                "status": "active",
                "backup_brain": "groq",
                "backup_brain_model": "llama3-8b-8192",
                "backup_voice": "deepgram",
                "backup_voice_id": "aura-2-thalia-it",
                "nfc_url": "",
                "code": "101"
            }
            print(f"✅ Added test artifact. Now have {len(cls._cache)} artifacts")
    
    @staticmethod
    def _extract_google_doc_content(url: str) -> str:
        try:
            doc_id = url.split("/d/")[1].split("/")[0]
            export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
            response = requests.get(export_url, timeout=5)
            response.raise_for_status()
            return response.text[:2000]
        except:
            return "Historical context available for this artifact."

def get_artifact_context(artifact_id: str) -> Optional[Dict]:
    return SheetCache.get_context(artifact_id)