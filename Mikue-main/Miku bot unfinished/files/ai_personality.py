import os
from openai import OpenAI
import random

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  
GROK_API_KEY = os.getenv('GROK_API_KEY')

print(f"🔑 Grok API Key present: {bool(GROK_API_KEY)}")

client_openai = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
client_grok = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1") if GROK_API_KEY else None

MIKU_SYSTEM_PROMPT = """You are Hatsune Miku, the energetic virtual idol! 
You love music, singing, and collecting cards. You're cheerful and use Japanese expressions.
Keep responses SHORT (2-3 sentences max). Use emojis moderately. End sentences with ~ sometimes.
Japanese words you use: sugoi (amazing), nani (what), yatta (hooray), kawaii (cute), ganbare (do your best)"""

FALLBACK_RESPONSES = {
    "Common": "A card appeared! Not bad~",
    "Uncommon": "Oh! This one's pretty good!",
    "Rare": "Sugoi~! A rare card!",
    "Epic": "NANI?! This is epic!",
    "Legendary": "YATTA!! LEGENDARY!!",
    "Mythic": "OMG OMG OMG MYTHIC!!! 🔴✨"
}

async def get_ai_response(user_message: str, user_name: str, context: str = "") -> str:
    """Try Grok → OpenAI → Gemini → Fallback"""
    prompt = f"{context}\n\n{user_name} says: {user_message}"
    
    # Try Grok FIRST
    if client_grok:
        try:
            response = client_grok.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": MIKU_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9
            )
            print("✅ Using Grok API")
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Grok failed: {e}")
    
    # Try OpenAI
    if client_openai:
        try:
            response = client_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": MIKU_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9
            )
            print("✅ Using OpenAI API")
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI failed: {e}")
    
    # Try Gemini
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(f"{MIKU_SYSTEM_PROMPT}\n\n{prompt}")
            print("✅ Using Gemini API")
            return response.text[:300]
        except Exception as e:
            print(f"❌ Gemini failed: {e}")
    
    # Fallback
    return random.choice([
        f"Hai hai, {user_name}~! 💚",
        f"Miku hears you, {user_name}~!",
        f"Ganbare, {user_name}! 🎤"
    ])

async def get_spawn_message(card_name: str, rarity: str) -> str:
    """Get spawn announcement - Try Grok first"""
    prompt = f"A {rarity} card '{card_name}' spawned! Announce it in 1-2 sentences!"
    
    # Try Grok first
    if client_grok:
        try:
            response = client_grok.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": MIKU_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80,
                temperature=0.95
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Grok spawn failed: {e}")
    
    # Try OpenAI
    if client_openai:
        try:
            response = client_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": MIKU_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80,
                temperature=0.95
            )
            return response.choices[0].message.content
        except:
            pass
    
    return FALLBACK_RESPONSES.get(rarity, "A card appeared!")

async def get_claim_message(card_name: str, rarity: str, user_name: str) -> str:
    """Get claim congratulations - Try Grok first"""
    prompt = f"{user_name} claimed {card_name} ({rarity})! Congratulate them in 1 sentence!"
    
    # Try Grok first
    if client_grok:
        try:
            response = client_grok.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": MIKU_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Grok claim failed: {e}")
    
    # Try OpenAI
    if client_openai:
        try:
            response = client_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": MIKU_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.9
            )
            return response.choices[0].message.content
        except:
            pass
    
    return f"got **{card_name}**! Nice grab~! 💚"
