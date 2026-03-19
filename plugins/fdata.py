import random
from telethon import events
from DARK.fdata import FLIRT_LINES
import config
from database import is_banned, get_maintenance, is_sudo

# Internal memory to prevent repetition
LAST_SENT_INDICES = []
MAX_MEMORY = 40

@events.register(events.NewMessage(pattern=r"^\.flirt(?:\s+(.*))?"))
async def flirt_handler(event):
    if event.fwd_from:
        return

    user_id = event.sender_id
    global LAST_SENT_INDICES

    # 1. BAN LOGIC CHECK
    if await is_banned(user_id):
        if user_id != config.OWNER_ID:
            return await event.edit("`YOU WERE BANNED BY OWNER!`")

    # 2. MAINTENANCE LOGIC CHECK
    if await get_maintenance():
        if user_id != config.OWNER_ID and not await is_sudo(user_id):
            return await event.edit("`System is under Maintenance Mode.`")

    # 3. TARGETING LOGIC
    reply = await event.get_reply_message()
    input_str = event.pattern_match.group(1)

    if reply:
        target_id = reply.sender_id
    elif input_str:
        try:
            user = await event.client.get_entity(input_str)
            target_id = user.id
        except Exception:
            return await event.edit("`Error: Target not found!`")
    else:
        return await event.edit("`Usage: Reply to someone or provide a username!`")

    # 4. ADVANCED RANDOM LOGIC (40 lines memory)
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

    # 5. INVINCIBLE MENTION & EXECUTION
    mention = f"[\u2063](tg://user?id={target_id})"
    response_text = f"{FLIRT_LINES[chosen_index]} {mention}"
    
    await event.edit(response_text)

async def setup(client):
    client.add_event_handler(flirt_handler)
