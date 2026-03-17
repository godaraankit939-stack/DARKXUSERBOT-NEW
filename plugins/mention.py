import asyncio
import random
import requests
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- CONFIG ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"
# Expanded Emoji List
EMOJIS = [
    "🔥", "✨", "💀", "⚡", "🌟", "🛡️", "👑", "💎", "🎯", "🚀", 
    "🦁", "🦾", "🖤", "❄️", "👺", "🧿", "🌀", "🩸", "🧊", "🛸", 
    "🪐", "🎭", "🗡️", "🚩", "🎸", "🎰", "🧨", "🧿", "🔱"
]

def get_remote_aura():
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except: pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

# ================= TAG & MENTION LOGIC =================

@events.register(events.NewMessage(pattern=r"\.tagall(?:all|e| e)? ?(.*)"))
async def tagger_cmd(event):
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura = get_remote_aura()
        for line in random.sample(aura, 3):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode.`")

    if not event.is_group:
        return await event.edit("`Error: This command only works in groups!`")

    cmd = event.text.split()[0]
    args = event.pattern_match.group(1).strip()
    await event.delete() 

    members = []
    async for user in event.client.iter_participants(event.chat_id):
        if not user.bot:
            members.append(user)

    for i in range(0, len(members), 5):
        chunk = members[i:i+5]
        mention_text = ""
        for user in chunk:
            prefix = random.choice(EMOJIS) if ("e" in cmd or "alle" in cmd) else ""
            if user.username:
                mention_text += f"{prefix} @{user.username} "
            else:
                mention_text += f"{prefix} [{user.first_name}](tg://user?id={user.id}) "
        
        final_msg = f"{mention_text}\n{args}" if args else mention_text
        await event.respond(final_msg)
        await asyncio.sleep(2)

@events.register(events.NewMessage(pattern=r"\.mention ?(.*)"))
async def mention_cmd(event):
    # 🛡️ NO ENTRY / SECURITY
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura = get_remote_aura()
        for line in random.sample(aura, 3):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode.`")

    input_str = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    
    # Targeting Logic
    target_user = None
    text_to_send = ""

    if reply:
        target_user = await event.client.get_entity(reply.sender_id)
        text_to_send = input_str if input_str else "Hehe"
    elif input_str:
        parts = input_str.split(" ", 1)
        try:
            target_user = await event.client.get_entity(parts[0])
            text_to_send = parts[1] if len(parts) > 1 else "Hehe"
        except:
            return await event.edit("`Error: Invalid user or username!`")
    
    if not target_user:
        return await event.edit("`Error: Reply to someone or provide a username!`")

    # Emoji Selection
    emoji = random.choice(EMOJIS)
    
    # Creating Mention Link
    if target_user.username:
        mention = f"[{text_to_send}](tg://user?id={target_user.id})"
        final_mention = f"{emoji} {mention}"
    else:
        mention = f"[{text_to_send}](tg://user?id={target_user.id})"
        final_mention = f"{emoji} {mention}"

    await event.edit(final_mention)

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(tagger_cmd)
    client.add_event_handler(mention_cmd)
      
