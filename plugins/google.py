import asyncio
import random
import requests
from bs4 import BeautifulSoup
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- GITHUB CONFIG (Aura Lines) ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

def get_remote_aura():
    """Fetches aura lines with a timeout to ensure bot stability."""
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except Exception:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

@events.register(events.NewMessage(pattern=r"\.google ?(.*)"))
async def google_search(event):
    client = event.client
    me = await client.get_me()

    # 🛡️ 1. NO ENTRY LOGIC (Forceful Edit for Unauthorized Users)
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        selected_aura = random.sample(aura_list, min(3, len(aura_list)))
        for line in selected_aura:
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # 🛠️ 2. BAN CHECK
    if await is_banned(event.sender_id):
        return

    # 🛠️ 3. MAINTENANCE CHECK
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode Active.`")

    # 🛠️ 4. AUTHORIZATION (Owner/Sudo Only)
    if event.sender_id != me.id and not await is_sudo(event.sender_id):
        return

    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.edit("`Error: Please provide a search query.`")

    await event.edit(f"`🔍 Multi-Engine Search: {query}...`")
    
    final_info = ""

    # 🚀 ENGINE 1: GOOGLE DEEP SCRAPE
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        g_url = "https://www.google.com/search?q=" + query.replace(' ', '+') + "&hl=en"
        g_res = requests.get(g_url, headers=headers, timeout=10)
        soup = BeautifulSoup(g_res.text, "html.parser")
        
        g_results = []
        for g in soup.find_all("div", class_="VwiC3b"):
            text = g.get_text().strip()
            if text and text not in g_results:
                g_results.append(text)
        
        if g_results:
            final_info = "\n\n".join(g_results[:4])
    except Exception:
        pass

    # 🚀 ENGINE 2: WIKIPEDIA FALLBACK
    if not final_info or len(final_info) < 100:
        try:
            w_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(' ', '_')
            w_res = requests.get(w_url, timeout=10).json()
            if "extract" in w_res:
                final_info = w_res["extract"]
        except Exception:
            pass

    # 🚀 ENGINE 3: DUCKDUCKGO FINAL FALLBACK
    if not final_info or len(final_info) < 50:
        try:
            d_url = "https://api.duckduckgo.com/?q=" + query.replace(' ', '+') + "&format=json&no_html=1"
            d_res = requests.get(d_url, timeout=10).json()
            if d_res.get("AbstractText"):
                final_info = d_res["AbstractText"]
        except Exception:
            pass

    # --- FINAL OUTPUT ---
    if not final_info:
        return await event.edit("`Error: No results found after scanning all engines.`")

    # Building response safely to avoid f-string literal errors
    header_text = "🧐 **Search Results for:** `" + query.upper() + "`\n\n"
    footer_text = "\n\n**Powered By DARK-USERBOT** 💀"
    
    response_msg = header_text + "📝 " + final_info + footer_text
    
    # Telegram character limit check
    if len(response_msg) > 4095:
        response_msg = response_msg[:4090] + "..."

    await event.edit(response_msg)

async def setup(client):
    client.add_event_handler(google_search)
