import asyncio
import random
import requests
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID
import os

# --- CONFIG ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_remote_aura():
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except Exception:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

# ================= THE ALL-IN-ONE AI (.ASK) =================
@events.register(events.NewMessage(pattern=r"\.ask ?(.*)"))
async def ask_gemini(event):
    client = event.client

    # 🛡️ 1. NO ENTRY LOGIC (5s Forceful Edit)
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        selected_aura = random.sample(aura_list, min(3, len(aura_list)))
        for line in selected_aura:
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # 🛠️ 2. BAN & MAINTENANCE & SUDO CHECK
    if await is_banned(event.sender_id):
        return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode Active.`")

    query = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()

    # Reply logic for text
    if not query and reply:
        query = reply.text
    
    if not query:
        return await event.edit("`Error: Kuch toh pucho? (e.g. .ask Latest news of India)`")

    if not GEMINI_API_KEY:
        return await event.edit("`❌ Error: GEMINI_API_KEY Missing in Config!`")

    await event.edit("`🤖 Scanning Universe & Thinking...`")

    try:
        # 🚀 STABLE ENDPOINT: Gemini 1.5 Flash (V1)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        
        # Adding a system instruction for better results
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Answer concisely and provide latest information if asked. Query: {query}"
                }]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        data = res.json()

        # Error Handling for API
        if res.status_code != 200:
            err_msg = data.get('error', {}).get('message', 'Unknown API Error')
            return await event.edit(f"**⚠️ Gemini Error ({res.status_code}):**\n`{err_msg}`")

        # Result Extraction
        if "candidates" in data and data["candidates"][0]["content"]["parts"]:
            ans = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Clean Output
            final_output = (
                f"🤖 **AI Response:**\n\n"
                f"{ans}\n\n"
                f"**DARK-USERBOT** 💀"
            )
            
            # Telegram character limit handling
            if len(final_output) > 4095:
                # Agar output bada hai toh file me bhej sakte hain, par abhi cut kar rahe
                await event.edit(final_output[:4090] + "...")
            else:
                await event.edit(final_output)
        else:
            await event.edit("`⚠️ Gemini is silent. Check your query or API quota.`")

    except Exception as e:
        await event.edit(f"❌ `System Error: {str(e)}`")

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(ask_gemini)
    
