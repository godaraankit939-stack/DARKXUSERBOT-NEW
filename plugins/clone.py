import asyncio
import random
import os
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest, GetUserPhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- CONFIG & SHIELD ---
PROTECTED_USERNAME = "WILDxMSD"
ORIGINAL_DATA = {} 

# Remote Aura Helper (No-Entry ke liye zaroori)
def get_remote_aura():
    try:
        import requests
        AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"
        response = requests.get(AURA_URL)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except: pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

async def setup(client):
    @client.on(events.NewMessage(pattern=r"\.clone(?: |$)(.*)"))
    async def identity_clone(event):
        me = await event.client.get_me()
        
        # 🛡️ 1. NO ENTRY LOGIC (Forceful Edit)
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            aura_list = get_remote_aura()
            for line in random.sample(aura_list, min(3, len(aura_list))):
                await event.edit(line)
                await asyncio.sleep(1.5)
            return 

        # 🎯 TARGET EXTRACTION (Fix: Target define karna pehle)
        user_input = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        target = reply.sender_id if reply else user_input
        
        if not target:
            return await event.edit("`Error: Target provide karein ya reply karein.`")

        # 🚫 2. IDENTITY SHIELD (Strict ID Check)
        try:
            target_obj = await event.client.get_entity(target)
            if target_obj.id == OWNER_ID and event.sender_id != me.id:
                shield_lines = [
                    "👑 **The Sun is only one. You cannot mirror the Sun.**",
                    "⚜️ **Master's legacy is encrypted. No one can copy the Sun.**"
                ]
                return await event.edit(random.choice(shield_lines))
        except: pass

        # 🛠️ 3. BAN & MAINTENANCE CHECK
        if await is_banned(event.sender_id): return
        if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
            return await event.edit("🛠 **Maintenance Mode is ON.**")

        if event.sender_id != me.id: return 

        # 📦 BACKUP ORIGINAL DATA
        if not ORIGINAL_DATA:
            full_me = await event.client(GetFullUserRequest(me.id))
            ORIGINAL_DATA['first_name'] = me.first_name or ""
            ORIGINAL_DATA['last_name'] = me.last_name or ""
            ORIGINAL_DATA['about'] = full_me.full_user.about or ""

        await event.edit("`🔄 Cloning Identity... Please wait.`")
        
        try:
            full_user = await event.client(GetFullUserRequest(target))
            user = full_user.users[0]
            user_bio = getattr(full_user.full_user, 'about', "") or ""
            
            await event.client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=user_bio
            ))
            
            photo = await event.client.download_profile_photo(user)
            if photo:
                uploaded_photo = await event.client.upload_file(photo)
                await event.client(UploadProfilePhotoRequest(file=uploaded_photo))
                if os.path.exists(photo): os.remove(photo)
            
            await event.edit(f"✅ **Identity Cloned Successfully!**")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")

    # --- REVERT COMMAND ---
    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def identity_revert(event):
        me = await event.client.get_me()
        if event.sender_id != me.id: return
        if not ORIGINAL_DATA:
            return await event.edit("`❌ No backup found!`")

        await event.edit("`🔄 Reverting Identity...`")
        try:
            await event.client(UpdateProfileRequest(
                first_name=ORIGINAL_DATA['first_name'],
                last_name=ORIGINAL_DATA['last_name'],
                about=ORIGINAL_DATA['about']
            ))
            photos = await event.client(GetUserPhotosRequest(user_id=me.id, offset=0, max_id=0, limit=1))
            if photos.photos:
                await event.client(DeletePhotosRequest(id=[photos.photos[0]]))
            await event.edit("✅ **Identity Restored!** 👑")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")
        
