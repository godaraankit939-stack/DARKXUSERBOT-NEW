import asyncio
import random
import requests
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- CONFIG & SHIELD ---
PROTECTED_USERNAME = "WILDxMSD"
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

def get_remote_aura():
    try:
        response = requests.get(AURA_URL)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️", "⌬ `System: God Mode Active` ✨"]

async def setup(client):
    # --- MAGIC CLONE COMMAND ---
    @client.on(events.NewMessage(pattern=r"\.clone(?: |$)(.*)"))
    async def identity_clone(event):
        me = await event.client.get_me()

        # 🛡️ 1. NO ENTRY LOGIC (Owner's Chat Protection)
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            aura_list = get_remote_aura()
            selected_aura = random.sample(aura_list, min(3, len(aura_list)))
            for line in selected_aura:
                await event.edit(line)
                await asyncio.sleep(1.5)
            return

        # 🚫 2. IDENTITY SHIELD (Anti-Cloning for MSD)
        user_input = event.pattern_match.group(1).strip()
        if PROTECTED_USERNAME in user_input or user_input == f"@{PROTECTED_USERNAME}":
            if event.sender_id != me.id:
                shield_lines = [
                    "👑 **The King is only one. You cannot mirror the Sun.**",
                    "⚜️ **Master's legacy is encrypted. No one can copy the King.**"
                ]
                await event.edit(random.choice(shield_lines))
                return

        # 🛠️ 3. BAN CHECK
        if await is_banned(event.sender_id):
            return

        # 🛠️ 4. MAINTENANCE CHECK
        if await get_maintenance():
            if event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
                return await event.edit("🛠 **Maintenance Mode is ON.**")

        # Command Execution (Only for Master)
        if event.sender_id != me.id: return 

        reply = await event.get_reply_message()
        target = reply.sender_id if reply else user_input
        
        if not target:
            return await event.edit("`Bhulaaaa! Target toh do? Kiski copy karni hai?`")

        await event.edit("`🔄 Cloning Identity... Please wait.`")
        
        try:
            full_user = await event.client(GetFullUserRequest(target))
            user = full_user.users[0]
            photo = await event.client.download_profile_photo(user)
            
            await event.client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=full_user.about or ""
            ))
            
            if photo:
                await event.client(UploadProfilePhotoRequest(await event.client.upload_file(photo)))
            
            await event.edit(f"✅ **Identity Cloned Successfully!**\n`Bhulaaaa Mode: Active` 🎭")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")

    # --- REVERT COMMAND ---
    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def identity_revert(event):
        me = await event.client.get_me()

        # NO ENTRY Logic
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            return # Silent exit for others

        if event.sender_id != me.id: return

        await event.edit("`🔄 Reverting to Original Master Identity...`")
        try:
            # Reverting Name, Last Name and Bio to MSD defaults
            await event.client(UpdateProfileRequest(
                first_name="Ankit", 
                last_name="👑", 
                about="Master of DARK-USERBOT 💀 | @WILDxMSD"
            ))
            await event.edit("✅ **Identity Restored! The Real Master is back.** 👑")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")
  
