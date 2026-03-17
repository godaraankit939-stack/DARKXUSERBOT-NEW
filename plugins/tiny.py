import asyncio
import os
import subprocess
from PIL import Image
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

CONVERTER_BOT = "@toWebmBot"  # ya @VideoStickerzBot

# ================= TINY CMD =================
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
            "`Please reply to a photo or a sticker to use this command professionally.`"
        )

    reply = await event.get_reply_message()

    # 🎯 VALIDATION
    if not reply.photo and not reply.sticker:
        return await event.edit(
            "`Please reply to a photo or a sticker to use this command professionally.`"
        )

    await event.edit("`⚡ Processing...`")

    input_path = None
    output_file = None

    try:
        # 📥 DOWNLOAD
        input_path = await reply.download_media()

        # ================= PHOTO =================
        if reply.photo:
            img = Image.open(input_path).convert("RGB")

            w, h = img.size
            img = img.resize((max(1, w // 2), max(1, h // 2)), Image.LANCZOS)

            output_file = "tiny.jpg"
            img.save(output_file, "JPEG", quality=90)

            await client.send_file(
                event.chat_id,
                output_file,
                reply_to=event.reply_to_msg_id
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

        # ================= ANIMATED STICKER =================
        else:
            resized_video = "tiny.mp4"

            # 🎞️ Resize via ffmpeg
            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", input_path,
                "-vf", "scale=iw/2:ih/2",
                resized_video
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 🤖 Send to converter bot
            await client.send_file(CONVERTER_BOT, resized_video)

            # ⏳ wait for bot response
            await asyncio.sleep(7)

            msgs = await client.get_messages(CONVERTER_BOT, limit=1)

            if not msgs or not msgs[0].sticker:
                return await event.edit("`Conversion bot failed. Try again.`")

            # 📤 Send final sticker back
            await client.send_file(
                event.chat_id,
                msgs[0].media,
                reply_to=event.reply_to_msg_id
            )

        await event.delete()

    except Exception as e:
        await event.edit(f"`Error: {str(e)}`")

    finally:
        # 🧹 CLEANUP
        try:
            if input_path and os.path.exists(input_path):
                os.remove(input_path)

            for f in ["tiny.jpg", "tiny.webp", "tiny.mp4"]:
                if os.path.exists(f):
                    os.remove(f)

        except:
            pass


# ================= SETUP =================
async def setup(client):
    client.add_event_handler(tiny_handler)
