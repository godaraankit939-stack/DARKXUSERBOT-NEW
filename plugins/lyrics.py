import asyncio
import random
import requests
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

@events.register(events.NewMessage(pattern=r"\.lyrics ?(.*)"))
async def lyrics_handler(event):
    client = event.client
    me = await client.get_me()

    # 🛡️ 1. NO ENTRY LOGIC (Professional Style)
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        for line in random.sample(aura_list, min(3, len(aura_list))):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # 🛠️ 2. BAN & MAINTENANCE CHECK
    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`Status: Maintenance Mode Active.`")

    song_name = event.pattern_match.group(1).strip()
    if not song_name:
        return await event.edit("`Error: Please provide a song name!`")

    await event.edit(f"`🎵 Searching lyrics for: {song_name}...`")

    try:
        # 🚀 Direct Lyrics API (No Google Scraping)
        # Using a reliable public API for faster results
        url = f"https://lyrist.vercel.app/api/{song_name.replace(' ', '%20')}"
        response = requests.get(url, timeout=10).json()

        if "lyrics" not in response or not response["lyrics"]:
            return await event.edit("`Error: Lyrics not found for this song.`")

        title = response.get("title", song_name.upper())
        artist = response.get("artist", "Unknown Artist")
        lyrics_text = response["lyrics"]

        # 📋 Formatting: Professional Code Box Format
        # Hum lyrics ko monospace me rakhenge taaki help menu jaisa look aaye
        header = f"╔══════════════════╗\n║  ❁ 𝖫𝖸𝖱𝖨𝖢𝖲 𝖥𝖮𝖴𝖭𝖣 ❁  ║\n╚══════════════════╝\n"
        meta = f"➶ **Song:** `{title}`\n➶ **Artist:** `{artist}`\n\n"
        
        # Code format wrapper
        formatted_lyrics = f"```\n{lyrics_text}\n```"
        
        final_output = f"{header}{meta}{formatted_lyrics}\n\n**Powered By DARK-USERBOT** 💀"

        # Telegram character limit check
        if len(final_output) > 4096:
            await event.edit("`Lyrics are too long! Sending as a snippet...`")
            final_output = f"{header}{meta}
http://googleusercontent.com/immersive_entry_chip/0

### 📋 Is Code Mein Kya Alag Hai?
1.  **Non-Google Fetching:** Hum `lyrist` API ka use kar rahe hain jo seedha text format mein lyrics deta hai, isliye "No Result" aane ke chances kam hain.
2.  **Compact Code Format:** Lyrics ko ` ``` ` (triple backticks) mein dala gaya hai. Isse font chota aur professional dikhta hai, bilkul tumhare help menu ki tarah.
3.  **Header Styling:** Ek professional box header dala hai jo DARK-USERBOT ki theme se match karta hai.
4.  **Security Layers:** No-Entry, Ban check aur Timeout isme bhi integrated hain.

Ankit, ab ise deploy karke check karo. Kya ab `.lyrics` ka look aur response waisa hi hai jaisa tum chahte the?

**Batao, ab agla panna konsa kholna hai? Humne info, lyrics, aur triple-engine google sab set kar diya hai.** 🚀🔥

http://googleusercontent.com/action_card_content/1
                 
