import random
import config
import asyncio
from telethon import events
# 🛡️ Sakt Check: Fdata path loading
try:
    from DARK.fdata import FLIRT_LINES
except Exception as e:
    try:
        from plugins.fdata import FLIRT_LINES
    except:
        FLIRT_LINES = ["Oye hoye! 😉", "Tum kitni pyaari ho! ❤️"] # Fallback agar file na mile
        print(f"⚠️ Warning: fdata file nahi mili! Error: {e}")

from database import is_banned, get_maintenance, is_sudo

# Memory to prevent repetition
LAST_SENT_INDICES = []
MAX_MEMORY = 40

async def flirt_handler(event):
    # Public command logic: fwd messages ko ignore karo
    if event.fwd_from:
        return

    user_id = event.sender_id
    global LAST_SENT_INDICES

    # 1. OWNER/SUDO Bypass (Owner hamesha use kar sakta hai)
    is_owner = (user_id == config.OWNER_ID)
    is_s = await is_sudo(user_id)

    # 2. BAN CHECK (Public users ke liye)
    if not is_owner and not is_s:
        if await is_banned(user_id):
            return # Banned users ko reply tak nahi dena
        
        # 3. MAINTENANCE CHECK (Public users ke liye)
        if await get_maintenance():
            return await event.reply("🚧 **Bot is under Maintenance Mode.**")

    # 4. TARGETING LOGIC
    reply = await event.get_reply_message()
    input_str = event.pattern_match.group(1)

    if reply:
        target_id = reply.sender_id
    elif input_str:
        try:
            # Username se ID nikalne ke liye
            user = await event.client.get_entity(input_str)
            target_id = user.id
        except Exception:
            return await event.reply("❌ **Error:** Target user nahi mila!")
    else:
        return await event.reply("ℹ️ **Usage:** Reply to someone or use `.flirt @username`")

    # 5. RANDOM LOGIC
    total_lines = len(FLIRT_LINES)
    all_indices = list(range(total_lines))
    available_indices = [i for i in all_indices if i not in LAST_SENT_INDICES]

    if not available_indices:
        LAST_SENT_INDICES.clear()
        available_indices = all_indices

    chosen_index = random.choice(available_indices)
    LAST_SENT_INDICES.append(chosen_index)
    
    if len(LAST_SENT_INDICES) > MAX_MEMORY:
        LAST_SENT_INDICES.pop(0)

    # 6. EXECUTION (Public hai isliye event.reply use karo, edit nahi)
    mention = f"[\u2063](tg://user?id={target_id})"
    response_text = f"{FLIRT_LINES[chosen_index]} {mention}"
    
    # Agar tumne khud likha hai toh edit karega, warna reply karega
    if event.out:
        await event.edit(response_text)
    else:
        await event.reply(response_text)

async def setup(client):
    # Pattern: .flirt ya .flirt @username dono pakdega
    client.add_event_handler(
        flirt_handler, 
        events.NewMessage(pattern=r"^\.flirt(?:\s+(.*))?")
    )
    print("✅ Flirt Plugin (Public) Loaded Successfully!")
    
