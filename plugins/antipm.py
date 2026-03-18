import asyncio
import random
from telethon import events, functions
from database import (
    is_banned, get_maintenance, is_approved, 
    approve_user, disapprove_user, get_antipm_status,
    is_warned_in_db, set_warned_in_db, delete_warned_user, 
    set_antipm_status, is_sudo
)
from config import OWNER_ID

# --- NO ENTRY HELPER (Aura Lines) ---
def get_remote_aura():
    try:
        import requests
        AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except: pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

# ================= 1. PM GUARD HANDLER (The Action) =================
@events.register(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def antipm_handler(event):
    client = event.client
    sender_id = event.sender_id
    
    # 🛡️ NO ENTRY LOGIC (Owner DM Protection)
    if event.chat_id == OWNER_ID and sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        selected_aura = random.sample(aura_list, min(3, len(aura_list)))
        for line in selected_aura:
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # Security & Status Checks
    if await is_banned(sender_id): return
    if not await get_antipm_status(): return 

    # 👑 APG LOGIC (THE GOD MODE)
    # Agar Owner message kare, toh Anti-PM useless hai.
    if sender_id == OWNER_ID:
        # Respect message for the Lord
        respect_lines = [
            "✨ `My Lord MSD is here... I must bow down in silence.` 👑",
            "👑 `The King has arrived! Anti-PM protocols are now deactivated for my Lord.`",
            "🔱 `Presence of the Supreme detected. Welcome, My Lord.`"
        ]
        await event.reply(random.choice(respect_lines))
        return # Process killed for Owner

    # Normal Checks (Sudos are also exempt)
    if event.is_bot or await is_sudo(sender_id) or await is_approved(sender_id):
        return

    # --- WARN & BLOCK LOGIC (Sakt Rules) ---
    if not await is_warned_in_db(sender_id):
        # 1st Warning
        warn_msg = (
            "**⌬ 𝖠𝖭𝖳𝖨-𝖯𝖬 𝖲𝖤𝖢𝖴𝖱𝖨𝖳𝖸** 🛡️\n\n"
            "⚠️ `Warning:` Unauthorized DM detected!\n"
            "I don't talk to strangers. If you message again without approval, you will be **BLOCKED** instantly.\n\n"
            "**Status:** `First & Final Warning` 🚨"
        )
        await event.reply(warn_msg)
        await set_warned_in_db(sender_id)
    else:
        # 2nd Attempt: Instant Block
        try:
            await client(functions.contacts.BlockRequest(id=sender_id))
            await delete_warned_user(sender_id)
            # Notify in logs or current chat if needed
        except Exception:
            pass

# ================= 2. PM CONTROL COMMANDS (Public) =================
@events.register(events.NewMessage(pattern=r"^\.(antipm|approve|disapprove|a|da) ?(.*)"))
async def antipm_cmd_handler(event):
    # Ban & Maintenance Check
    if await is_banned(event.sender_id):
        return await event.edit("`YOU WERE BANNED BY OWNER!`")
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`🛠️ System Status: Maintenance Mode Active.`")

    cmd = event.pattern_match.group(1).lower()
    args = event.pattern_match.group(2).strip().lower()
    
    # Logic for ON/OFF
    if cmd == "antipm":
        if args == "on":
            await set_antipm_status(True)
            await event.edit("🛡️ **Anti-PM Security: ACTIVATED**")
        elif args == "off":
            await set_antipm_status(False)
            await event.edit("🔓 **Anti-PM Security: DEACTIVATED**")
        else:
            await event.edit("`Usage: .antipm on/off`")
    
    # Logic for Approve/Disapprove
    elif cmd in ["approve", "a"]:
        reply = await event.get_reply_message()
        target = reply.sender_id if reply else (int(args) if args.isdigit() else None)
        if not target: return await event.edit("`Reply to user or give ID!`")
        await approve_user(target)
        await event.edit(f"✅ **Approved User:** `{target}`")
        
    elif cmd in ["disapprove", "da"]:
        reply = await event.get_reply_message()
        target = reply.sender_id if reply else (int(args) if args.isdigit() else None)
        if not target: return await event.edit("`Reply to user or give ID!`")
        await disapprove_user(target)
        await event.edit(f"❌ **Disapproved User:** `{target}`")

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(antipm_handler)
    client.add_event_handler(antipm_cmd_handler)
    
