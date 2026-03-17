import asyncio
import random
import requests
from bs4 import BeautifulSoup
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

# ================= GOOGLE CMD (DEEP SCRAPE) =================
@events.register(events.NewMessage(pattern=r"\.google ?(.*)"))
async def google_search(event):
    client = event.client
    me = await client.get_me()

    # 🛡️ NO ENTRY LOGIC
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        for line in random.sample(aura_list, min(3, len(aura_list))):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode Active.`")
    if event.sender_id != me.id and not await is_sudo(event.sender_id): return

    query = event.pattern_match.group(1).strip()
    if not query: return await event.edit("`Error: Search query toh do?`")

    await event.edit(f"`🔍 Scanning Engines for: {query}...`")

    final_info = ""
    try:
        # 🚀 ENGINE 1: DuckDuckGo HTML (Better than JSON API)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}", headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        
        snippets = [s.get_text().strip() for s in soup.find_all("a", class_="result__snippet")[:5]]
        if snippets:
            final_info = "\n\n".join(snippets)
    except Exception: pass

    # 🚀 ENGINE 2: Wikipedia Fallback
    if not final_info or len(final_info) < 60:
        try:
            w_res = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}", timeout=10).json()
            if w_res.get("extract"): final_info = w_res["extract"]
        except Exception: pass

    if not final_info:
        return await event.edit("`❌ Error: No results found. Try a different query.`")

    output = f"🧐 **Search Results for:** `{query.upper()}`\n\n📝 {final_info}\n\n**Powered By DARK-USERBOT** 💀"
    
    if len(output) > 4095: output = output[:4090] + "..."
    await event.edit(output)


# ================= ASK AI (GEMINI PRO FIX) =================
@events.register(events.NewMessage(pattern=r"\.ask ?(.*)"))
async def ask_ai(event):
    client = event.client
    me = await client.get_me()

    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID: return
    if event.sender_id != me.id and not await is_sudo(event.sender_id): return

    query = event.pattern_match.group(1).strip()
    if not query: return await event.edit("`Ask something to AI...`")

    if not GEMINI_API_KEY:
        return await event.edit("`❌ Error: GEMINI_API_KEY missing in Config!`")

    await event.edit("`🤖 AI is thinking...`")

    try:
        # Gemini 1.5 Flash - Using v1beta for better API key compatibility
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": query}]}]}
        
        res = requests.post(url, json=payload, timeout=30)
        data = res.json()

        if res.status_code != 200:
            err_msg = data.get('error', {}).get('message', 'Unknown Error')
            return await event.edit(f"**⚠️ Gemini Error ({res.status_code}):**\n`{err_msg}`")

        if "candidates" in data:
            ans = data["candidates"][0]["content"]["parts"][0]["text"]
            final_ans = f"🤖 **AI Response:**\n\n{ans}\n\n**Powered By DARK-USERBOT** 💀"
            
            if len(final_ans) > 4095: final_ans = final_ans[:4090] + "..."
            await event.edit(final_ans)
        else:
            await event.edit("`⚠️ Gemini not responding. Key check karein.`")

    except Exception as e:
        await event.edit(f"`❌ System Error: {str(e)}`")


# ================= SETUP =================
async def setup(client):
    client.add_event_handler(google_search)
    client.add_event_handler(ask_ai)
                 
