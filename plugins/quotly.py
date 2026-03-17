import asyncio
import random
import requests
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
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

# ================= QUOTE LOGIC (.Q) =================

@events.register(events.NewMessage(pattern=r"\.q ?(.*)"))
async def quotly_cmd(event):
    # 🛡️ 1. NO ENTRY LOGIC
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura = get_remote_aura()
        for line in random.sample(aura, 3):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # 🛠️ 2. SECURITY CHECKS
    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode.`")

    reply = await event.get_reply_message()
    if not reply:
        return await event.edit("`Error: Reply to a message to quote it!`")

    # 🚀 Start Processing
    await event.delete() # Speed of light: delete cmd
    
    bot = "@QuotLyBot"
    async with event.client.conversation(bot) as conv:
        try:
            # Step 1: Forward/Send message to Quotly
            response = conv.wait_event(events.NewMessage(incoming=True, from_users=bot))
            await event.client.forward_messages(bot, reply)
            
            # Step 2: Wait for sticker
            response = await response
            
            # Step 3: Send the sticker back to original chat
            if response.sticker:
                await event.client.send_file(event.chat_id, response.message)
            else:
                await event.client.send_message(event.chat_id, "`Error: Quotly didn't respond with a sticker.`")
                
            # 🧹 EVIDENCE CLEANUP: Delete chat history with Quotly
            await event.client(functions.messages.DeleteHistoryRequest(
                peer=bot,
                max_id=0,
                just_clear=False,
                revoke=True
            ))

        except YouBlockedUserError:
            return await event.respond(f"`Error: Please unblock {bot} first!`")
        except Exception as e:
            return await event.respond(f"`Error: {str(e)}`")

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(quotly_cmd)
                                  
