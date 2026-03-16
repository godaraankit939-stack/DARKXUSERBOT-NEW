import asyncio
import random
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- GITHUB CONFIG (Aura Lines) ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

async def setup(client):
    @client.on(events.NewMessage(pattern=r"\.bcast(?: |$)(.*)"))
    async def broadcast_handler(event):
        me = await event.client.get_me()

        # 🛡️ 1. NO ENTRY LOGIC (Forceful Edit in Owner's Chat)
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            import requests
            try:
                r = requests.get(AURA_URL)
                aura_list = [l.strip() for l in r.text.split('\n') if l.strip()]
            except:
                aura_list = ["**⌬ 𝖠𝖢𝖤𝖲𝖲 𝖣𝖤𝖭𝖨𝖤𝖣** 🛡️"]
            
            selected_aura = random.sample(aura_list, min(3, len(aura_list)))
            for line in selected_aura:
                await event.edit(line)
                await asyncio.sleep(1.5)
            return

        # 🛠️ 2. BAN CHECK
        if await is_banned(event.sender_id):
            return

        # 🛠️ 3. MAINTENANCE CHECK
        if await get_maintenance():
            if event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
                return await event.edit("🛠 **Maintenance Mode is ON.**")

        # Command Execution (Only for Master/Client)
        if event.sender_id != me.id: return

        msg_content = event.pattern_match.group(1).strip()
        reply_to_msg = await event.get_reply_message()

        if not msg_content and not reply_to_msg:
            return await event.edit("`Bhulaaaa! Please provide text or reply to a message.`")

        # ⚠️ STEP 1: HIGH RISK WARNING & CONFIRMATION
        warning_msg = (
            "⚠️ **𝖧𝖨𝖦𝖧 𝖱𝖨𝖲𝖪 𝖶𝖠𝖱𝖭𝖨𝖭𝖦** ⚠️\n\n"
            "◈ `This action has 80-90% chances of Account Ban.`\n"
            "◈ `Are you sure you want to proceed?`\n\n"
            "👉 Send: `Yes, i am sure` to start.\n"
            "👉 Send: `Cancel` to stop.\n\n"
            "⏳ **𝖳𝗂𝗆𝖾𝗈𝗎𝗍:** `1 Minute`"
        )
        await event.edit(warning_msg)

        # 🛠️ 4. CONVERSATION LOGIC (Waiting for Confirmation)
        async with event.client.conversation(event.chat_id) as conv:
            try:
                response = await conv.get_response(timeout=60)
                if response.text == "Yes, i am sure":
                    await event.respond("✅ **𝖢𝗈𝗇𝖿𝗂𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝖱𝖾𝖼𝖾𝗂𝗏𝖾𝖽. 𝖲𝗍𝖺𝗋𝗍𝗂𝗇𝗀...**")
                elif response.text.lower() == "cancel":
                    return await event.respond("❌ **𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽 𝖻𝗒 𝖴𝗌𝖾𝗋.**")
                else:
                    return await event.respond("⚠️ **𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖱𝖾𝗌𝗉𝗈𝗇𝗌𝖾. 𝖢𝗈𝗆𝗆𝖺𝗇𝖽 𝖡𝗅𝗈𝖼𝗄𝖾𝖽.**")
            except asyncio.TimeoutError:
                return await event.respond("⏰ **𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍 𝖺𝗎𝗍𝗈-𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽 𝖿𝗈𝗋 𝗌𝖺𝖿𝖾𝗍𝗒.**")

        # 🚀 STEP 2: ACTUAL BROADCAST
        await event.respond("🚀 **𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍𝗂𝗇𝗀 𝗂𝗇 𝗉𝗋𝗈𝗀𝗋𝖾𝗌𝗌...**")
        
        count = 0
        error = 0
        async for dialog in event.client.iter_dialogs():
            try:
                # 🛠️ 5. ANTI-BAN LOGIC (1.5s Sleep)
                if reply_to_msg:
                    await event.client.send_message(dialog.id, reply_to_msg)
                else:
                    await event.client.send_message(dialog.id, msg_content)
                count += 1
                await asyncio.sleep(1.5) 
            except Exception:
                error += 1
                continue

        await event.respond(f"✅ **𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍 𝖥𝗂𝗇𝗂𝗌𝗁𝖾𝖽!**\n◈ **𝖲𝖾𝗇𝗍:** `{count}`\n◈ **𝖥𝖺𝗂𝗅𝖾𝖽:** `{error}`")
              
