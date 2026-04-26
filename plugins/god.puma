import os
import asyncio
import random
from telethon import events, functions, types
from telethon.tl.functions.account import UpdateStatusRequest
from telethon.tl.functions.channels import GetParticipantRequest

# --- DATABASE & CONFIG ---
from config import OWNER_ID
from database import is_banned, get_maintenance, is_sudo

GOD_MODE = False
AUTH_CHATS = ["D4RK_ARMYY", "dark_uploads"] 

async def can_use(event):
    user_id = event.sender_id
    if user_id == OWNER_ID or await is_sudo(user_id): return True
    if await is_banned(user_id) or await get_maintenance(): return False
    return True

# --- THE MASTER COMMAND ---
@events.register(events.NewMessage(pattern=r"\.god$"))
async def toggle_god(event):
    global GOD_MODE
    if not await can_use(event): return
    if event.sender_id != (await event.client.get_me()).id: return

    if not GOD_MODE:
        GOD_MODE = True
        asyncio.create_task(freeze_status(event.client))
        await event.edit("🔱 **GOD MODE: ACTIVATED**\n`Stealth: Full Dark Mode`")
    else:
        GOD_MODE = False
        await event.client(UpdateStatusRequest(offline=False))
        await event.edit("🔱 **GOD MODE: DEACTIVATED**\n`Status: Back to Online` 🟢")

async def freeze_status(client):
    while GOD_MODE:
        try:
            # ❄️ LAST SEEN FREEZE: Server ko offline signal bhejna
            await client(UpdateStatusRequest(offline=True))
        except: pass
        await asyncio.sleep(15)

# --- THE DARK LOGIC (SEEN & VC NO-ENTRY) ---

# 1. 🚫 SEEN BLOCKER (Phantom Read)
@events.register(events.Raw)
async def seen_blocker(event):
    if not GOD_MODE: return
    # Agar Telegram seen mangne ki koshish karega (ReadHistory), 
    # toh hum usey process hi nahi hone denge. No Double Tick.
    if isinstance(event, (types.UpdateReadHistoryOutbox, types.UpdateReadHistoryInbox)):
        raise events.StopPropagation

# 2. 🚷 VC NO-ENTRY LOGIC (Invincible ID)
@events.register(events.Raw)
async def vc_no_entry(event):
    if not GOD_MODE: return
    # Jab bhi VC activity detect hogi
    if isinstance(event, (types.UpdateGroupCallParticipants, types.UpdateGroupCall)):
        try:
            # API JUGAD: 'JoinAs' metadata ko empty ya peer-less rakhna
            await event._client(functions.phone.JoinGroupCallRequest(
                call=event.call,
                join_as=types.InputPeerSelf(),
                muted=True,
                video_stopped=True,
                invite_hash="" # Empty hash for ghost entry
            ))
        except: pass

# 3. 🎭 TYPING SPOOF (Choosing Sticker / Playing Game)
@events.register(events.NewMessage(outgoing=True))
async def activity_spoof(event):
    if not GOD_MODE: return
    if event.text.startswith("."): return 
    actions = [types.SendMessageGamePlayAction(), types.SendMessageChooseStickerAction()]
    await event.client(functions.messages.SetTypingRequest(
        peer=event.input_chat, 
        action=random.choice(actions)
    ))

# 4. 🖼️ VIEW-ONCE AUTO-SAVE
@events.register(events.NewMessage(incoming=True))
async def vo_capture(event):
    if not GOD_MODE: return
    if event.media and hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds:
        file = await event.download_media()
        await event.client.send_file("me", file, caption="🖼️ **God View-Once Capture**")
        if os.path.exists(file): os.remove(file)

# --- SETUP ---
def setup(client):
    client.add_event_handler(toggle_god)
    client.add_event_handler(seen_blocker)
    client.add_event_handler(vc_no_entry)
    client.add_event_handler(activity_spoof)
    client.add_event_handler(vo_capture)
    
