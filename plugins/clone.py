import asyncio
import random
import os
from telethon import events, functions, types
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

async def setup(client):
    @client.on(events.NewMessage(pattern=r"\.clone(?: |$)(.*)"))
    async def identity_clone(event):
        me = await event.client.get_me()
        if event.sender_id != me.id: return

        user_input = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        target = reply.sender_id if reply else user_input
        
        if not target:
            return await event.edit("`❌ Error: Reply to a user or provide ID.`")

        # 👑 SPG SHIELD
        try:
            target_obj = await event.client.get_entity(target)
            if target_obj.id == OWNER_ID:
                return await event.edit("👑 **The Sun is only one. You cannot mirror the Sun.**")
        except: pass

        await event.edit("`☠️Cloning target...`")

        # 1. GET FULL TARGET DATA (Force Call)
        full_user = await event.client(GetFullUserRequest(target))
        user = full_user.users[0]
        user_bio = full_user.full_user.about or ""
        target_first = user.first_name or ""
        target_last = user.last_name or ""

        # 2. BACKUP ME
        full_me = await event.client(GetFullUserRequest(me.id))
        ORIGINAL_DATA.update({
            'first_name': me.first_name or "",
            'last_name': me.last_name or "",
            'about': full_me.full_user.about or ""
        })
        await save_original_profile(me.id, me.first_name, me.last_name, full_me.full_user.about)

        # 3. UPDATE NAME & BIO (Direct)
        await event.client(UpdateProfileRequest(
            first_name=target_first,
            last_name=target_last,
            about=user_bio
        ))
        
        # 4. FORCE PFP CLONE
        # Telegram handles letters/emojis automatically if no photo is uploaded.
        # But for actual photos, we use high-quality download.
        photo = await event.client.download_profile_photo(user, file="clone_pfp.jpg")
        
        if photo:
            uploaded_photo = await event.client.upload_file(photo)
            await event.client(UploadProfilePhotoRequest(file=uploaded_photo))
            if os.path.exists(photo): os.remove(photo)
            await event.edit(f"✅ **Cloned Successfully: {target_first}**")
        else:
            # Agar ID par koi photo hi nahi hai (sirf letter hai)
            await event.edit(f"✅ **Cloned!** (Target has no PFP)")

    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def identity_revert(event):
        me = await event.client.get_me()
        if event.sender_id != me.id: return

        data = ORIGINAL_DATA or await get_original_profile(me.id)
        if not data:
            return await event.edit("`❌ No backup found!`")

        await event.edit("`🔄 Restoring Original Identity...`")
        
        # Restore Name & Bio
        await event.client(UpdateProfileRequest(
            first_name=data['first_name'],
            last_name=data['last_name'],
            about=data['about']
        ))
        
        # Restore PFP: Delete the cloned one
        photos = await event.client(GetUserPhotosRequest(user_id=me.id, offset=0, max_id=0, limit=1))
        if photos.photos:
            await event.client(DeletePhotosRequest(id=[photos.photos[0]]))
        
        await event.edit("✅ **Original Identity Restored!** 👑")
        
