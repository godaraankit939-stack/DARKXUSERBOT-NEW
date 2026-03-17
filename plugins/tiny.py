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
    
    # Validation
    if not reply or not (reply.sticker or reply.photo):
        return await event.edit("`Error: Reply to a static sticker or photo!`")
    
    # Animated Sticker check (Advanced safety)
    if reply.sticker and reply.sticker.animated:
        return await event.edit("`Error: Animated stickers (TGS/Video) are not supported by Tiny.`")

    status = await event.edit("`🖌️ Processing...`")

    try:
        # 📂 Step 1: Download to BytesIO (In-memory)
        media_bytes = await event.client.download_media(reply, file=io.BytesIO())
        media_bytes.seek(0)
        
        # 🛠️ Step 2: Open and Convert for Identification Fix
        img = Image.open(media_bytes).convert("RGBA")
        width, height = img.size
        
        # 📉 Step 3: Recursive Resizing (Reduce by 50%)
        # Logic: Ensuring it stays at least 1px to avoid crash
        new_width = max(1, int(width / 2))
        new_height = max(1, int(height / 2))
        
        # Using LANCZOS for high quality downscaling
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 💾 Step 4: Saving based on original format
        output_bytes = io.BytesIO()
        
        if reply.sticker:
            # Re-saving as WebP for Sticker effect
            resized_img.save(output_bytes, format="WEBP")
            output_bytes.seek(0)
            await event.client.send_file(
                event.chat_id, 
                output_bytes, 
                reply_to=reply, 
                force_document=False
            )
        else:
            # Saving as PNG for Photos
            resized_img.save(output_bytes, format="PNG")
            output_bytes.seek(0)
            await event.client.send_file(
                event.chat_id, 
                output_bytes, 
                reply_to=reply, 
                force_document=False
            )

        await status.delete()

    except Exception as e:
        await event.edit(f"❌ `Advanced Error: {str(e)}`")

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(tiny_image_cmd)
            
