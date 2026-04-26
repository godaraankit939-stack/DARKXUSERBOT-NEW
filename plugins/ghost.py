import os
import asyncio
import random
from telethon import events, functions, types
from telethon.tl.functions.account import UpdateStatusRequest
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

# --- DATABASE & CONFIG ---
from config import OWNER_ID
from database import is_banned, get_maintenance, is_sudo

# --- GLOBALS ---
GHOST_MODE = False
AUTH_CHATS = ["D4RK_ARMYY", "dark_uploads"] 

# --- SAKT AUTH & MAINTENANCE LOGIC ---
async def can_use(event):
    user_id = event.sender_id
    # Owner aur Sudo ko koi nahi rok sakta
    if user_id == OWNER_ID or await is_sudo(user_id):
        return True
    # Ban aur Maintenance Check
    if await is_banned(user_id):
        return False
    if await get_maintenance():
        return False
    # Force Join Check
    for chat in AUTH_CHATS:
        try:
            await event.client(GetParticipantRequest(channel=chat, participant=user_id))
        except UserNotParticipantError:
            await event.reply(f"❌ **Join @{chat} to use Ghost Mode!**")
            return False
        except: continue
    return True

# --- TOGGLE COMMAND ---
@events.register(events.NewMessage(pattern=r"\.ghost$"))
async def toggle_ghost(event):
    global GHOST_MODE
    if not await can_use(event): return
    if event.sender_id != (await event.client.get_me()).id: return

    if not GHOST_MODE:
        GHOST_MODE = True
        asyncio.create_task(freeze_status(event.client))
        await event.edit("👻 **GHOST MODE: ACTIVATED**\n\n"
                         "✅ **Seen:** Hidden (Single Tick)\n"
                         "✅ **Status:** Frozen (Offline)\n"
                         "✅ **Typing:** Spoofed (Game/Sticker)\n"
                         "✅ **VC:** Invincible Mode Enabled")
    else:
        GHOST_MODE = False
        await event.client(UpdateStatusRequest(offline=False))
        await event.edit("👻 **GHOST MODE: DEACTIVATED**\n`Status: Back to Online` 🟢")

async def freeze_status(client):
    while GHOST_MODE:
        try:
            # Server ko hamesha offline status bhejte raho
            await client(UpdateStatusRequest(offline=True))
        except: pass
        await asyncio.sleep(15)

# --- INVINCIBLE GHOST LOGIC ---

# 1. SEEN OFF (Phantom Read)
# Isme code koi request nahi bhejta, isliye Telegram ko 'Read' ka pata hi nahi chalta.

# 2. TYPING SPOOF (Choosing Sticker / Playing Game)
@events.register(events.NewMessage(outgoing=True))
async def typing_spoof(event):
    if not GHOST_MODE: return
    if event.text.startswith("."): return 
    
    # Typing ke waqt shaant nahi rahega, ye statuses flash honge
    actions = [
        types.SendMessageGamePlayAction(),
        types.SendMessageChooseStickerAction()
    ]
    await event.client(functions.messages.SetTypingRequest(
        peer=event.input_chat,
        action=random.choice(actions)
    ))

# 3. GHOST VC (No Entry Logic)
@events.register(events.NewMessage(pattern=r"\.gvc$"))
async def ghost_vc(event):
    if not await can_use(event): return
    if not GHOST_MODE: return await event.edit("`Pehle .ghost on kar le bhai!`")
    
    await event.edit("`🛠️ Injecting No-Entry Stealth in VC...`")
    try:
        # Invincible Join: Channel identity + No-video + Muted metadata
        await event.client(functions.phone.JoinGroupCallRequest(
            call=await event.client.get_input_entity(event.chat_id),
            join_as=await event.client.get_input_entity(event.chat_id),
            muted=True,
            video_stopped=True,
            invite_hash="" 
        ))
        await event.edit("👤 **VC Joined Invincibly.**\n`ID Hidden from active list.`")
    except Exception as e:
        await event.edit(f"❌ **VC Error:** `{e}`")

# 4. VIEW-ONCE AUTO-SAVE (Sakt Safety)
@events.register(events.NewMessage(incoming=True))
async def vo_capture(event):
    if not GHOST_MODE: return
    if event.media and hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds:
        file = await event.download_media()
        await event.client.send_file("me", file, caption="🖼️ **Ghost View-Once Capture**")
        if os.path.exists(file): os.remove(file)

# --- SETUP ---
def setup(client):
    client.add_event_handler(toggle_ghost)
    client.add_event_handler(typing_spoof)
    client.add_event_handler(ghost_vc)
    client.add_event_handler(vo_capture)
  
