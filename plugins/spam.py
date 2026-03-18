import asyncio
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- DYNAMIC SUDO IMPORT FROM DARK FOLDER ---
try:
    from DARK.sudos import SUDO_USERS
except ImportError:
    SUDO_USERS = []

# --- SPG LINES ---
OWNER_LINE = "👑 **The King (MSD) is present. Lower your head and your commands.**"
SUDO_LINE = "👑 **This is the Throne of MSD. Your commands mean nothing.**"

# Global Flag for Force Stop
SPAM_RUNNING = True

# ================= 1. .spam [Count] [Text] =================
@events.register(events.NewMessage(pattern=r"\.spam (\d+) (.*)"))
async def fast_spam(event):
    global SPAM_RUNNING
    # 🛡️ BAN & MAINTENANCE LOGIC
    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID: return
    
    count = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)
    
    await event.delete()
    SPAM_RUNNING = True
    
    for _ in range(count):
        if not SPAM_RUNNING: break
        await event.client.send_message(event.chat_id, text)
        await asyncio.sleep(0.5)

# ================= 2. .dmspam [Count] [Target] [Text] =================
@events.register(events.NewMessage(pattern=r"\.dmspam (\d+) (.*)"))
async def dm_spam_cmd(event):
    global SPAM_RUNNING
    # 🛡️ BAN & MAINTENANCE LOGIC
    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID: return

    count = int(event.pattern_match.group(1))
    input_str = event.pattern_match.group(2)
    
    reply = await event.get_reply_message()
    
    # Target Selection Logic
    if reply:
        target = reply.sender_id
        text = input_str
    else:
        parts = input_str.split(maxsplit=1)
        if len(parts) < 2:
            return await event.edit("`.dmspam [count] [@username] [text]`")
        target = parts[0]
        text = parts[1]

    try:
        user = await event.client.get_entity(target)
        u_id = user.id

        # ⚔️ SPG PROTECTION CHECK
        if u_id == OWNER_ID:
            return await event.edit(OWNER_LINE)
        if u_id in SUDO_USERS:
            return await event.edit(SUDO_LINE)

        await event.delete()
        SPAM_RUNNING = True
        
        for _ in range(count):
            if not SPAM_RUNNING: break
            # 🚫 NO MENTION - DIRECT MESSAGE
            await event.client.send_message(u_id, text)
            await asyncio.sleep(0.7)
            
    except Exception as e:
        await event.edit(f"❌ `DM Error: {str(e)}`")

# ================= 3. .fsspam (Force Stop) =================
@events.register(events.NewMessage(pattern=r"\.fsspam$"))
async def force_stop_spam(event):
    global SPAM_RUNNING
    SPAM_RUNNING = False
    await event.edit("`🛑 ALL SPAM TASKS STOPPED IMMEDIATELY!`")
    await asyncio.sleep(1.5)
    await event.delete()

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(fast_spam)
    client.add_event_handler(dm_spam_cmd)
    client.add_event_handler(force_stop_spam)
  
