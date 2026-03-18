import asyncio
import os
from PIL import Image
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

@events.register(events.NewMessage(pattern=r"\.tiny$"))
async def tiny_handler(event):
    client = event.client

    # 🛡️ 1. NO-ENTRY (OWNER DM PROTECTION)
    if event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        await event.edit("**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤▣** 🛡️")
        return

    # 🚫 2. BAN LOGIC (FIXED)
    if await is_banned(event.sender_id):
        await event.edit("`YOU WERE BANNED BY OWNER!`")
        return

    # 🛠️ 3. MAINTENANCE LOGIC (FIXED)
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        await event.edit("`🛠️ System Status: Maintenance Mode Active.`")
        return

    # 📩 REPLY CHECK
    if not event.is_reply:
        return await event.edit("`Please reply to a photo or a sticker.`")

    reply = await event.get_reply_message()
    if not reply.photo and not reply.sticker:
        return await event.edit("`Reply to a photo or sticker.`")

    await event.edit("`⚡ Processing Tiny Image...`")

    input_path = None
    output_file = None

    try:
        input_path = await reply.download_media()
        img = Image.open(input_path)
        
        # Dimensions Fix: Aadhaar logic (Dhoti Faad Scaling)
        w, h = img.size
        new_w = max(50, w // 2)
        new_h = int(h * (new_w / w))

        img = img.resize((new_w, new_h), Image.LANCZOS)

        # ================= OUTPUT HANDLING =================
        if reply.sticker:
            output_file = "tiny.webp"
            img = img.convert("RGBA")
            img.save(output_file, "WEBP")
        else:
            output_file = "tiny.png"
            img = img.convert("RGB")
            img.save(output_file, "PNG")

        # Send as Image (not doc)
        await client.send_file(
            event.chat_id,
            output_file,
            reply_to=reply.id,
            force_document=False
        )
        await event.delete()

    except Exception as e:
        await event.edit(f"`Error: {str(e)}`")
    finally:
        if input_path and os.path.exists(input_path): os.remove(input_path)
        if output_file and os.path.exists(output_file): os.remove(output_file)

async def setup(client):
    client.add_event_handler(tiny_handler)
    
