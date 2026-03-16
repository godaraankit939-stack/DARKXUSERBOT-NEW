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
ORIGINAL_DATA = {} # Temp backup for Revert

async def setup(client):
    @client.on(events.NewMessage(pattern=r"\.clone(?: |$)(.*)"))
    async def identity_clone(event):
        me = await event.client.get_me()
        
                # 🛡️ 1. NO ENTRY LOGIC (Forceful Edit)
        # MSD ki chat mein agar koi aur command likhe toh Aura Edit chalu
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            aura_list = get_remote_aura()
            for line in random.sample(aura_list, 3):
                await event.edit(line)
                await asyncio.sleep(1.5)
            return # Yahan cmd khatam, aage kuch nahi chalega

        # 🚫 2. IDENTITY SHIELD (Strict ID Check)
        try:
            # Target nikalne ka logic (is se pehle target define hona chahiye)
            target_obj = await event.client.get_entity(target)
            
            # Agar target Owner (MSD) hai aur chalane wala koi aur hai
            if target_obj.id == OWNER_ID and event.sender_id != me.id:
                shield_lines = [
                    "👑 **The Sun is only one. You cannot mirror the Sun.**",
                    "⚜️ **Master's legacy is encrypted. No one can copy the Sun.**"
                ]
                return await event.edit(random.choice(shield_lines))
        except Exception as e:
            # Agar target invalid hai toh error dikhao ya ignore karo
            pass 

        # 🛠️ 3. BAN & MAINTENANCE CHECK
        if await is_banned(event.sender_id): return
        if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
            return await event.edit("🛠 **Maintenance Mode is ON.**")

        if event.sender_id != me.id: return 

        # 📦 BACKUP ORIGINAL DATA (Pehli baar clone par)
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
            
            # Update Name & Bio
            await event.client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=user_bio
            ))
            
            # Update Photo
            photo = await event.client.download_profile_photo(user)
            if photo:
                uploaded_photo = await event.client.upload_file(photo)
                await event.client(UploadProfilePhotoRequest(file=uploaded_photo))
                if os.path.exists(photo): os.remove(photo)
            
            await event.edit(f"✅ **Identity Cloned Successfully!**\n`Bhulaaaa Mode: Active` 🎭")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")

    # --- REVERT COMMAND ---
    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def identity_revert(event):
        me = await event.client.get_me()
        if event.sender_id != me.id: return

        if not ORIGINAL_DATA:
            return await event.edit("`❌ No backup found! Try cloning someone first.`")

        await event.edit("`🔄 Reverting to Original Identity...`")
        try:
            # 1. Restore Name & Bio
            await event.client(UpdateProfileRequest(
                first_name=ORIGINAL_DATA['first_name'],
                last_name=ORIGINAL_DATA['last_name'],
                about=ORIGINAL_DATA['about']
            ))
            
            # 2. Restore Photo (Delete Clone PFP first)
            photos = await event.client(GetUserPhotosRequest(user_id=me.id, offset=0, max_id=0, limit=1))
            if photos.photos:
                await event.client(DeletePhotosRequest(id=[photos.photos[0]]))
            
            await event.edit("✅ **Identity Restored! The Sun is back.** 👑")
        except Exception as e:
            await event.edit(f"❌ **Error:** `{e}`")
        
