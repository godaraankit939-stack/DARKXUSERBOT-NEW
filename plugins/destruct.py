import asyncio
import os
import random
from telethon import events, functions, types
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- GITHUB CONFIG (Aura Lines) ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

def get_remote_aura():
    try:
        import requests
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

@events.register(events.NewMessage(pattern=r"\.ss$"))
async def secret_saver(event):
    client = event.client
    me = await client.get_me()

    # 🛡️ 1. NO ENTRY LOGIC (Protects Owner's Space)
    # If someone else tries to trigger this in the Owner's PM
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        for line in random.sample(aura_list, 3):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # 🛠️ 2. BAN CHECK
    if await is_banned(event.sender_id): 
        return
        
    # 🛠️ 3. MAINTENANCE CHECK (Bypassed by Owner and Sudo)
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("🚧 **System is currently under maintenance.**")

    # 🎯 TARGET VALIDATION
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.edit("`Error: Please reply to a 'View Once' or destructing media.`")

    await event.edit("`⚙️ Processing Secret Media...`")

    try:
        # Download media to a temporary local path
        file_path = await client.download_media(reply)
        
        if file_path:
            # Send to the Saved Messages of the user who triggered the command
            # Peer 'me' refers to the Saved Messages of the current session
            caption = (
                "✅ **Secret Media Captured Successfully**\n\n"
                f"◈ **Source:** `{event.chat_id}`\n"
                "◈ **Storage:** `Personal Cloud (Saved Messages)`"
            )
            await client.send_file("me", file_path, caption=caption)
            
            # Delete file from local storage immediately after sending
            if os.path.exists(file_path):
                os.remove(file_path)
            
            await event.edit("✅ **Media has been saved to your Saved Messages.**")
        else:
            await event.edit("❌ **Extraction Failed:** Unable to download media.")
            
    except Exception as e:
        await event.edit(f"❌ **Error:** `{str(e)}`")

# --- SETUP FUNCTION ---
async def setup(client):
    client.add_event_handler(secret_saver)
      
