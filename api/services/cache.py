import time
import hashlib
from typing import Optional, Dict

class TTSCache:
    _text_cache: Dict[str, Dict] = {}
    _audio_cache: Dict[str, Dict] = {}
    _max_items = 100
    _ttl = 86400  # 24 hours
    
    @classmethod
    def set(cls, key: str, text: str):
        if len(cls._text_cache) > cls._max_items:
            oldest = min(cls._text_cache, key=lambda k: cls._text_cache[k]["timestamp"])
            del cls._text_cache[oldest]
        
        cls._text_cache[key] = {
            "text": text,
            "timestamp": time.time()
        }
    
    @classmethod
    def get_text(cls, key: str) -> Optional[str]:
        item = cls._text_cache.get(key)
        if item and (time.time() - item["timestamp"] < cls._ttl):
            return item["text"]
        return None
    
    @classmethod
    def store_audio_url(cls, key: str, url: str):
        cls._audio_cache[key] = {
            "url": url,
            "timestamp": time.time()
        }
    
    @classmethod
    def get_audio_url(cls, key: str) -> Optional[str]:
        item = cls._audio_cache.get(key)
        if item and (time.time() - item["timestamp"] < cls._ttl):
            return item["url"]
        return None
    
    @classmethod
    def has_audio(cls, key: str) -> bool:
        return key in cls._audio_cache
    
    @classmethod
    def generate_key(cls, artifact_id: str, language: str, text: str) -> str:
        content = f"{artifact_id}:{language}:{text}"
        return hashlib.md5(content.encode()).hexdigest()

cache_tts = TTSCache()