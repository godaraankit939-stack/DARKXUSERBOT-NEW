import asyncio
import random
from telethon import events, functions
from database import (
    is_banned, get_maintenance, is_approved, 
    approve_user, disapprove_user, get_antipm_status,
    is_warned_in_db, set_warned_in_db, delete_warned_user, set_antipm_status, is_sudo
)
from config import OWNER_ID

# --- NO ENTRY HELPER ---
def get_remote_aura():
    try:
        import requests
        AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"
        response = requests.get(AURA_URL)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except: pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

# --- 1. ANTIPM MESSAGE HANDLER (The Action Logic) ---
@events.register(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def antipm_handler(event):
    client = event.client
    me = await client.get_me()

    # 🛡️ NO ENTRY LOGIC (Jo sahi kaam kar raha tha)
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        selected_aura = random.sample(aura_list, min(3, len(aura_list)))
        for line in selected_aura:
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # Security Checks
    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id): return

    # 🚨 ANTI-PM WORKING CHECK
    if not await get_antipm_status(): return 
    if event.sender_id == me.id or event.is_bot or await is_sudo(event.sender_id): return
    if await is_approved(event.sender_id): return 

    # --- WARN OR BLOCK LOGIC ---
    if not await is_warned_in_db(event.sender_id):
        # First Warning
        warn_text = (
            "**⌬ 𝖠𝖭𝖳𝖨-𝖯𝖬 𝖲𝖤𝖢𝖴𝖱𝖨𝖳𝖸** 🛡️\n\n"
            "`Unauthorized Access Detected!`\n"
            "Do not message me in PM without permission. This is your **first and final warning**.\n\n"
            "**Status:** `Last Warning` ⚠️"
        )
        await event.reply(warn_text)
        await set_warned_in_db(event.sender_id)
    else:
        # Second Message: Auto Block
        try:
            await client(functions.contacts.BlockRequest(id=event.sender_id))
            await delete_warned_user(event.sender_id)
            print(f"✅ User {event.sender_id} blocked by AntiPM.")
        except Exception as e:
            print(f"❌ Block Error: {e}")

# --- 2. ANTIPM COMMAND HANDLER (The Control Logic) ---
@events.register(events.NewMessage(outgoing=True, pattern=r"\.(antipm|approve|disapprove) ?(.*)"))
async def antipm_cmd_handler(event):
    me = await event.client.get_me()
    
    # Auth Check
    if event.sender_id != me.id and not await is_sudo(event.sender_id): return

    cmd = event.pattern_match.group(1)
    args = event.pattern_match.group(2).strip().lower()

    if cmd == "antipm":
        current_status = await get_antipm_status()
        if args == "on":
            if current_status:
                return await event.edit("🛡️ **AntiPM is already Activated!**")
            await set_antipm_status(True)
            await event.edit("🛡️ **AntiPM Activated Successfully!**")
        elif args == "off":
            if not current_status:
                return await event.edit("🔓 **AntiPM is already Deactivated!**")
            await set_antipm_status(False)
            await event.edit("🔓 **AntiPM Deactivated Successfully!**")
        else:
            await event.edit("`Usage: .antipm on/off`")
    
    elif cmd == "approve":
        reply = await event.get_reply_message()
        target = reply.sender_id if reply else args
        if not target: return await event.edit("`Error: Reply to a user or give ID.`")
        await approve_user(target)
        await event.edit(f"✅ **User {target} has been Approved.**")
        
    elif cmd == "disapprove":
        reply = await event.get_reply_message()
        target = reply.sender_id if reply else args
        if not target: return await event.edit("`Error: Reply to a user or give ID.`")
        await disapprove_user(target)
        await event.edit(f"❌ **User {target} Disapproved.**")

# --- SETUP FUNCTION ---
async def setup(client):
    client.add_event_handler(antipm_handler)
    client.add_event_handler(antipm_cmd_handler)
    
