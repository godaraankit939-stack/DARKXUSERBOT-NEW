import asyncio
import os
from PIL import Image
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

@events.register(events.NewMessage(pattern=r"\.tiny$"))
async def tiny_handler(event):
    client = event.client

    # 🚫 BAN CHECK
    if await is_banned(event.sender_id):
        return

    # 🛠️ MAINTENANCE
    if await get_maintenance() and event.sender_id != OWNER_ID:
        return await event.edit("`System Status: Maintenance Mode Active.`")

    # 📩 REPLY CHECK
    if not event.is_reply:
        return await event.edit(
            "`Please reply to a photo or a sticker.`"
        )

    reply = await event.get_reply_message()

    if not reply.photo and not reply.sticker:
        return await event.edit(
            "`Reply to a photo or sticker.`"
        )

    await event.edit("`⚡ Processing...`")

    input_path = None
    output_file = None

    try:
        input_path = await reply.download_media()

        # ================= PHOTO =================
        if reply.photo:
            img = Image.open(input_path).convert("RGB")

            w, h = img.size
            new_w, new_h = max(1, w // 2), max(1, h // 2)

            img = img.resize((new_w, new_h), Image.LANCZOS)

            output_file = "tiny.jpg"
            img.save(output_file, "JPEG", quality=95)

            # 🔥 PHOTO AS PHOTO (NO DOCUMENT)
            await client.send_file(
                event.chat_id,
                output_file,
                reply_to=event.reply_to_msg_id,
                attributes=[]  # force normal image
            )

        # ================= STATIC STICKER =================
        elif reply.sticker and reply.sticker.mime_type == "image/webp":
            img = Image.open(input_path).convert("RGBA")

            w, h = img.size
            img = img.resize((max(1, w // 2), max(1, h // 2)), Image.LANCZOS)

            output_file = "tiny.webp"
            img.save(output_file, "WEBP")

            await client.send_file(
                event.chat_id,
                output_file,
                reply_to=event.reply_to_msg_id
            )

        # ================= ANIMATED → STATIC STICKER =================
        else:
            # first frame extract
            img = Image.open(input_path)

            try:
                img.seek(0)
            except:
                pass

            img = img.convert("RGBA")

            w, h = img.size
            img = img.resize((max(1, w // 2), max(1, h // 2)), Image.LANCZOS)

            output_file = "tiny.webp"
            img.save(output_file, "WEBP")

            await client.send_file(
                event.chat_id,
                output_file,
                reply_to=event.reply_to_msg_id
            )

        await event.delete()

    except Exception as e:
        await event.edit(f"`Error: {str(e)}`")

    finally:
        try:
            if input_path and os.path.exists(input_path):
                os.remove(input_path)

            for f in ["tiny.jpg", "tiny.webp"]:
                if os.path.exists(f):
                    os.remove(f)

        except:
            pass


async def setup(client):
    client.add_event_handler(tiny_handler)
