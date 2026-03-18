import asyncio
import random
import os
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest, GetUserPhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from database import (
    get_maintenance, is_sudo, is_banned, 
    save_original_profile, get_original_profile
)
from config import OWNER_ID

# RAM-Based Backup (Fastest)
ORIGINAL_DATA = {} 

# Remote Aura Helper
def get_remote_aura():
    try:
        import requests
        AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except: pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

async def setup(client):
    @client.on(events.NewMessage(pattern=r"\.clone(?: |$)(.*)"))
    async def identity_clone(event):
        me = await event.client.get_me()
        
        # 🛡️ 1. NO ENTRY LOGIC
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            aura_list = get_remote_aura()
            for line in random.sample(aura_list, min(3, len(aura_list))):
                await event.edit(line)
                await asyncio.sleep(1.5)
            return 

        user_input = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        target = reply.sender_id if reply else user_input
        
        if not target:
            return await event.edit("`Error: Reply to a user or provide username/ID.`")

        # 👑 2. SPG LOGIC (THE GOD SHIELD)
        try:
            target_obj = await event.client.get_entity(target)
            if target_obj.id == OWNER_ID:
                shield_lines = [
                    "👑 **The Sun is only one. You cannot mirror the Sun.**",
                    "⚜️ **Master's legacy is encrypted. Access Denied.**"
                ]
                return await event.edit(random.choice(shield_lines))
        except: pass

        # Security Checks
        if await is_banned(event.sender_id): return
        if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
            return await event.edit("🛠 **Maintenance Mode is ON.**")

        if event.sender_id != me.id: return 

        # 📦 DOUBLE-SHIELD BACKUP (RAM + DATABASE)
        if not ORIGINAL_DATA:
            # Pehle DB mein check karo
            db_backup = await get_original_profile(me.id)
            if db_backup:
                ORIGINAL_DATA['first_name'] = db_backup['first_name']
                ORIGINAL_DATA['last_name'] = db_backup['last_name']
                ORIGINAL_DATA['about'] = db_backup['about']
            else:
                # Naya backup lo agar kahin nahi hai
                await event.edit("`📦 Creating First-Time Permanent Backup...`")
                full_me = await event.client(GetFullUserRequest(me.id))
                f_name = me.first_name or ""
                l_name = me.last_name or ""
                bio = full_me.full_user.about or ""
                
                # RAM Save
                ORIGINAL_DATA.update({'first_name': f_name, 'last_name': l_name, 'about': bio})
                # DB Save
                await save_original_profile(me.id, f_name, l_name, bio)

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
            
            await event.edit(f"✅ **Identity Cloned!**\n`Type .revert to restore.`")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")

    # --- REVERT COMMAND (The Fail-Safe Restore) ---
    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def identity_revert(event):
        me = await event.client.get_me()
        if event.sender_id != me.id: return

        # 📦 Data Retrieval Logic (RAM -> DB -> Error)
        data = ORIGINAL_DATA
        if not data:
            db_data = await get_original_profile(me.id)
            if db_data:
                data = db_data
                # Wapas RAM mein daal do future use ke liye
                ORIGINAL_DATA.update(db_data)

        if not data:
            return await event.edit("`❌ No backup found in RAM or Database!`")

        await event.edit("`🔄 Restoring Original Identity...`")
        try:
            await event.client(UpdateProfileRequest(
                first_name=data['first_name'],
                last_name=data['last_name'],
                about=data['about']
            ))
            
            # Delete the latest (cloned) profile photo
            photos = await event.client(GetUserPhotosRequest(user_id=me.id, offset=0, max_id=0, limit=1))
            if photos.photos:
                await event.client(DeletePhotosRequest(id=[photos.photos[0]]))
            
            await event.edit("✅ **Original Identity Restored!** 👑")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")
                
