import asyncio
import io
import random
import requests
from telethon import events
from PIL import Image
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- CONFIG ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

def get_remote_aura():
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except: pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

# ================= TINY IMAGE LOGIC =================

@events.register(events.NewMessage(pattern=r"\.tiny$"))
async def tiny_image_cmd(event):
    # 🛡️ 1. NO ENTRY LOGIC
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura = get_remote_aura()
        for line in random.sample(aura, 3):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # 🛠️ 2. BAN & MAINTENANCE & SUDO CHECK
    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode.`")

    reply = await event.get_reply_message()
    
    # 🚫 Strict Professional Validation (No Reply or Reply to non-media)
    if not reply or not (reply.sticker or reply.photo):
        return await event.edit("`❌ Error: Please reply to a photo or a static sticker to use this command professionally.`")
    
    # Check for Animated Media
    if reply.sticker and reply.sticker.animated:
        return await event.edit("`❌ Error: Animated media is not supported. Please reply to a static photo or sticker.`")

    await event.edit("`🖌️ Tinifying...`")

    try:
        # 📂 Step 1: Download to memory
        media_bytes = await event.client.download_media(reply, file=io.BytesIO())
        media_bytes.seek(0)
        
        # 🛠️ Step 2: PIL Processing
        img = Image.open(media_bytes)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        width, height = img.size
        # Recursive logic: 50% Reduction
        new_size = (max(1, width // 2), max(1, height // 2))
        img.thumbnail(new_size, Image.Resampling.LANCZOS)
        
        output_bytes = io.BytesIO()
        
        # 💾 Step 3: Format & Direct Send
        if reply.sticker:
            img.save(output_bytes, format="WEBP")
            output_bytes.seek(0)
            await event.client.send_file(
                event.chat_id, 
                output_bytes, 
                reply_to=reply
            )
        else:
            img.save(output_bytes, format="PNG")
            output_bytes.seek(0)
            # Direct Image Display (Not as file)
            await event.client.send_file(
                event.chat_id, 
                output_bytes, 
                reply_to=reply,
                force_document=False
            )

        await event.delete() # Speed of light deletion

    except Exception as e:
        await event.edit(f"❌ `Professional Error: {str(e)}`")

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(tiny_image_cmd)
        
