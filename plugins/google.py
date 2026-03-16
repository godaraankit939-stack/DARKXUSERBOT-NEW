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
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

@events.register(events.NewMessage(pattern=r"\.google ?(.*)"))
async def google_search(event):
    client = event.client
    me = await client.get_me()

    # 🛡️ 1. NO ENTRY LOGIC (Professional Forceful Edit)
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        selected_aura = random.sample(aura_list, min(3, len(aura_list)))
        for line in selected_aura:
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # 🛠️ 2. BAN & MAINTENANCE CHECK
    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("🚧 **System is under maintenance.**")

    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.edit("`Error: Kya search karna hai, Ankit? Query toh do.`")

    await event.edit(f"`🔍 Deep Searching: {query}...`")

    try:
        # 🌐 Deep Scrape Logic with Advanced Headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        url = f"https://www.google.com/search?q={query}&hl=en&gl=us"
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # 🎯 Extracting data from multiple containers to get 10-12 lines
        search_results = []
        
        # Section 1: Featured Snippet (Main answer)
        snippet = soup.find("div", class_="VwiC3b") or soup.find("span", class_="hgKElc")
        if snippet:
            search_results.append(snippet.get_text().strip())

        # Section 2: Related Questions / Knowledge Panel Snippets
        extra_data = soup.find_all("div", class_="yU79be")
        for item in extra_data[:2]:
            search_results.append(item.get_text().strip())

        # Section 3: Top 3 Search Result Descriptions
        descriptions = soup.find_all("div", class_="VwiC3b")
        for desc in descriptions[1:4]: # Pehle wale ke baad ke 3
            txt = desc.get_text().strip()
            if txt not in search_results:
                search_results.append(txt)

        # Merge results into a long explanation
        full_info = "\n\n".join(search_results)

        if len(full_info) < 50:
            return await event.edit("❌ **No Result Found:** Detailed data extract nahi ho paya.")

        # Final Formatting
        final_msg = (
            f"🧐 **Detailed Google Search Results:**\n\n"
            f"📝 {full_info}\n\n"
            f"**Powered By DARK-USERBOT** 💀"
        )
        
        # Telegram character limit handle
        if len(final_msg) > 4096:
            final_msg = final_msg[:4000] + "..."

        await event.edit(final_msg)

    except Exception as e:
        await event.edit(f"❌ **System Error:** `{str(e)}`")

# --- SETUP FUNCTION ---
async def setup(client):
    client.add_event_handler(google_search)
  
