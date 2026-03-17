import asyncio
import random
import requests
from telethon import events
from googletrans import Translator
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- CONFIG (Remote Aura) ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

def get_remote_aura():
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except Exception:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

# ================= TRANSLATE CMD =================
@events.register(events.NewMessage(pattern=r"\.tr ?([a-z]{2})? ?(.*)"))
async def translate_cmd(event):
    client = event.client

    # 🛡️ 1. NO ENTRY LOGIC (The one you liked from history)
    # Agar unknown user owner ko PM karega, toh 1.5s delay ke saath 3 edits honge
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        selected_aura = random.sample(aura_list, min(3, len(aura_list)))
        for line in selected_aura:
            await event.edit(line)
            await asyncio.sleep(1.5) # Forceful 4.5-5s total delay
        return

    # 🛠️ 2. BAN & MAINTENANCE CHECK
    if await is_banned(event.sender_id):
        return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode Active.`")

    # 🛠️ 3. TEXT EXTRACTION (Reply or Direct)
    dest_lang = event.pattern_match.group(1) or "hi"
    input_str = event.pattern_match.group(2).strip()
    reply = await event.get_reply_message()

    if not input_str and reply:
        text_to_tr = reply.text
    elif input_str:
        text_to_tr = input_str
    else:
        return await event.edit("`Error: Provide text or reply to a message!`")

    await event.edit(f"`🔠 Translating to {dest_lang.upper()}...`")

    try:
        # 🚀 Using the library you added in requirements
        translator = Translator()
        # translate(text, dest_language)
        result = translator.translate(text_to_tr, dest=dest_lang)
        
        # 📋 Clean Output
        final_msg = (
            f"📥 **Input:** `{text_to_tr[:50]}...`\n"
            f"📤 **Output ({dest_lang.upper()}):**\n`{result.text}`\n\n"
            f"**DARK-USERBOT** 💀"
        )
        await event.edit(final_msg)

    except Exception as e:
        await event.edit(f"❌ `Translation Error: {str(e)}`")

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(translate_cmd)
    
