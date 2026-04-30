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

# RAM-Based Backup
ORIGINAL_DATA = {} 

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

        try:
            target_obj = await event.client.get_entity(target)
            if target_obj.id == OWNER_ID:
                return await event.edit("👑 **The Sun is only one. You cannot mirror the Sun.**")
        except: pass

        if await is_banned(event.sender_id): return
        if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
            return await event.edit("🛠 **Maintenance Mode is ON.**")

        if event.sender_id != me.id: return 

        # 📦 BACKUP
        await event.edit("`📦 Backing up current profile...`")
        full_me = await event.client(GetFullUserRequest(me.id))
        f_name = me.first_name or ""
        l_name = me.last_name or ""
        bio = full_me.full_user.about or ""
        
        ORIGINAL_DATA.update({'first_name': f_name, 'last_name': l_name, 'about': bio})
        await save_original_profile(me.id, f_name, l_name, bio)

        await event.edit("`🔄 Cloning Identity... Please wait.`")
        
        try:
            full_user = await event.client(GetFullUserRequest(target))
            user = full_user.users[0]
            user_bio = getattr(full_user.full_user, 'about', "") or ""
            
            target_first = user.first_name or ""
            target_last = user.last_name or ""

            await event.client(UpdateProfileRequest(
                first_name=target_first,
                last_name=target_last,
                about=user_bio
            ))
            
            # 🖼️ Photo Clone (With NoneType Fix)
            photo = await event.client.download_profile_photo(user)
            if photo: # Sirf tabhi upload karega agar photo download hui
                uploaded_photo = await event.client.upload_file(photo)
                await event.client(UploadProfilePhotoRequest(file=uploaded_photo))
                if os.path.exists(photo): os.remove(photo)
            
            await event.edit(f"✅ **Identity Cloned!**\n`Name: {target_first} {target_last}`")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")

    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def identity_revert(event):
        me = await event.client.get_me()
        if event.sender_id != me.id: return

        data = ORIGINAL_DATA
        if not data:
            db_data = await get_original_profile(me.id)
            if db_data:
                data = db_data
                ORIGINAL_DATA.update(db_data)

        if not data:
            return await event.edit("`❌ No backup found!`")

        await event.edit("`🔄 Restoring Original Identity...`")
        try:
            await event.client(UpdateProfileRequest(
                first_name=data['first_name'],
                last_name=data['last_name'],
                about=data['about']
            ))
            # Photo delete wala kachra hata diya hai
            await event.edit("✅ **Original Identity Restored!** 👑")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")
                                 
