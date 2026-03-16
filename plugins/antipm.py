import asyncio
from telethon import events, functions
from database import (
    is_banned, get_maintenance, is_approved, 
    approve_user, disapprove_user, get_antipm_status,
    is_warned_in_db, set_warned_in_db, delete_warned_user, set_antipm_status
)
from config import OWNER_ID

# Universal Auth Check
async def is_authorized(event):
    return event.sender_id == OWNER_ID or await is_sudo(event.sender_id)

async def setup(client):

    # --- 1. ANTIPM HANDLER ---
    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def antipm_handler(event):
        # 🛡️ SECURITY & MAINTENANCE CHECK
        if await is_banned(event.sender_id):
            return
        # Maintenance mein agar bot hai toh PMs ignore honge (Owner/Sudo ko chhod kar)
        if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
            return

        # Check if AntiPM is ON globally
        if not await get_antipm_status(): 
            return 
            
        if event.sender_id == OWNER_ID or event.is_bot: 
            return
            
        if await is_approved(event.sender_id): 
            return 

        # --- LOGIC: WARN OR BLOCK ---
        if not await is_warned_in_db(event.sender_id):
            # FIRST WARNING
            warn_text = (
                "**⌬ 𝖠𝖭𝖳𝖨-𝖯𝖬 𝖲𝖤𝖢𝖴𝖱𝖨𝖳𝖸** 🛡️\n\n"
                "`Unauthorized Access Detected!`\n"
                "Do not message me in PM without permission. This is your **first and final warning**. "
                "One more message and you will be **Auto-Blocked**.\n\n"
                "**Status:** `Last Warning` ⚠️"
            )
            await event.reply(warn_text)
            await set_warned_in_db(event.sender_id)
        else:
            # SECOND MESSAGE: BLOCK
            block_text = (
                "**⌬ 𝖲𝖸𝖲▵𝖤𝖬 𝖡𝖫▮𝖢𝖪▵𝖣** 🚫\n\n"
                "`Access Denied!`\n"
                "You ignored the warning. You are now permanently blocked from this account.\n\n"
                "**Action:** `Permanent Block`\n"
                "**Goodbye!** 👋"
            )
            await event.reply(block_text)
            await client(functions.contacts.BlockRequest(id=event.sender_id))
            await delete_warned_user(event.sender_id)

    # --- 2. ANTIPM COMMANDS (.a on/off, .approve) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.(a|approve|disapprove) ?(.*)"))
    async def antipm_cmd_handler(event):
        # 🛡️ COMMAND SECURITY
        if await is_banned(event.sender_id): return
        if await get_maintenance() and event.sender_id != OWNER_ID:
            return await event.edit("🛠 **Maintenance Mode is ON.**")
        if not await is_authorized(event): return
        
        cmd = event.pattern_match.group(1)
        args = event.pattern_match.group(2)

        if cmd == "a":
            if args == "on":
                await set_antipm_status(True)
                await event.edit("🛡️ **AntiPM Activated!**")
            elif args == "off":
                await set_antipm_status(False)
                await event.edit("🔓 **AntiPM Deactivated!**")
        
        elif cmd == "approve":
            target = (await event.get_reply_message()).sender_id if event.is_reply else args
            if not target: return await event.edit("`Reply to a user or give ID.`")
            await approve_user(target)
            await event.edit(f"✅ **User {target} Approved.**")
            
        elif cmd == "disapprove":
            target = (await event.get_reply_message()).sender_id if event.is_reply else args
            await disapprove_user(target)
            await event.edit(f"❌ **User {target} Disapproved.**")
      
