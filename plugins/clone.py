import asyncio
import random
import os
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
    @client.on(events.NewMessage(pattern=r"\.clone(?: |$)(.*)"))
    async def identity_clone(event):
        me = await event.client.get_me()

        # 🛡️ 1. NO ENTRY LOGIC
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            aura_list = get_remote_aura()
            selected_aura = random.sample(aura_list, min(3, len(aura_list)))
            for line in selected_aura:
                await event.edit(line)
                await asyncio.sleep(1.5)
            return

        # 🚫 2. IDENTITY SHIELD (The Sun Logic)
        user_input = event.pattern_match.group(1).strip()
        if PROTECTED_USERNAME in user_input or user_input == f"@{PROTECTED_USERNAME}":
            if event.sender_id != me.id:
                shield_lines = [
                    "👑 **The Sun is only one. You cannot mirror the Sun.**",
                    "⚜️ **Master's legacy is encrypted. No one can copy the Sun.**"
                ]
                return await event.edit(random.choice(shield_lines))

        # 🛠️ 3. BAN & MAINTENANCE CHECK
        if await is_banned(event.sender_id): return
        if await get_maintenance():
            if event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
                return await event.edit("🛠 **Maintenance Mode is ON.**")

        if event.sender_id != me.id: return 

        reply = await event.get_reply_message()
        target = reply.sender_id if reply else user_input
        if not target: return await event.edit("`Bhulaaaa! Target toh do?`")

        await event.edit("`🔄 Cloning Identity... Please wait.`")
        
        try:
            full_user = await event.client(GetFullUserRequest(target))
            user = full_user.users[0]
            
            # Sakti 1: Secure Bio Extraction
            user_bio = getattr(full_user.full_user, 'about', "") or ""
            
            # Sakti 2: Update Profile Details
            await event.client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=user_bio
            ))
            
            # Sakti 3: Error-Proof Photo Upload
            photo = await event.client.download_profile_photo(user)
            if photo and os.path.exists(photo):
                uploaded_photo = await event.client.upload_file(photo)
                # Explicitly passing 'file' parameter to fix InputFile error
                await event.client(UploadProfilePhotoRequest(file=uploaded_photo))
                os.remove(photo)
            
            await event.edit(f"✅ **Identity Cloned Successfully!**\n`Bhulaaaa Mode: Active` 🎭")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")

    # --- REVERT COMMAND ---
    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def identity_revert(event):
        me = await event.client.get_me()
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            return 
        if event.sender_id != me.id: return

        await event.edit("`🔄 Reverting to Original Master Identity...`")
        try:
            await event.client(UpdateProfileRequest(
                first_name="Ankit", 
                last_name="👑", 
                about="Master of DARK-USERBOT 💀 | @WILDxMSD"
            ))
            await event.edit("✅ **Identity Restored!** 👑")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")
    
