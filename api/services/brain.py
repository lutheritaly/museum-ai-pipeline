import os
import requests
from typing import Dict, Optional

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class BrainRouter:
    @staticmethod
    def generate(
        context: Dict[str, str],
        user_input: Optional[str],
        language: str,
        provider: str = "groq",
        model: str = "llama3-8b-8192"
    ) -> str:
        
        system_prompt = f"""
        You are a warm, knowledgeable museum guide for {context.get('name', 'this artifact')}.
        Speak in {language.upper()}.
        Context: {context.get('context_text', '')}
        
        Rules:
        - Keep responses to 2 sentences max (approx 20-30 words)
        - Be emotionally engaging, warm, and human-like
        - Include one surprising or delightful detail
        - Never say you're an AI or a bot
        - Be conversational, not academic
        """
        
        user_prompt = user_input or f"Tell me about {context.get('name', 'this artifact')} in an engaging way."
        
        try:
            if provider.lower() == "groq":
                return BrainRouter._call_groq(system_prompt, user_prompt, model)
            elif provider.lower() == "openrouter":
                return BrainRouter._call_openrouter(system_prompt, user_prompt, model)
            elif provider.lower() == "gemini":
                return BrainRouter._call_gemini(system_prompt, user_prompt)
            else:
                return BrainRouter._call_groq(system_prompt, user_prompt, "llama3-8b-8192")
        except Exception as e:
            print(f"❌ Brain error: {e}")
            return f"Welcome to {context.get('name', 'this beautiful artifact')}. There's so much to discover here."
    
    @staticmethod
    def _call_groq(system: str, user: str, model: str) -> str:
        if not GROQ_API_KEY:
            raise Exception("GROQ_API_KEY not set")
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=8)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    
    @staticmethod
    def _call_openrouter(system: str, user: str, model: str) -> str:
        if not OPENROUTER_API_KEY:
            raise Exception("OPENROUTER_API_KEY not set")
            
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    
    @staticmethod
    def _call_gemini(system: str, user: str) -> str:
        if not GEMINI_API_KEY:
            raise Exception("GEMINI_API_KEY not set")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system}\n\n{user}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 100
            }
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()