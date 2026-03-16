import asyncio
import random
import requests
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# help_data.py se details lene ke liye
try:
    from plugins.help_data import PLUGINS_HELP
except ImportError:
    PLUGINS_HELP = {}

# --- GITHUB CONFIG ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

def get_remote_aura():
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵𝖨𝖤𝖣** 🛡️", "⌬ `System: God Mode Active` ✨"]

# --- YOUR PERFECTED HELP MENU ---
HELP_MENU = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     ⌬ DARK X USERBOT ⌬       ┃
┣━━━━━━━━━━━━┳━━━━━━━━━━━━━┫
┃ ◈ Afk        ┃ ◈ Animate     ┃
┃ ◈ Antipm     ┃ ◈ B-Cast      ┃
┃ ◈ Clone      ┃ ◈ Create      ┃
┃ ◈ Destruct   ┃ ◈ Dict        ┃
┃ ◈ Google     ┃ ◈ Info        ┃
┃ ◈ Lyrics     ┃ ◈ Memify      ┃
┃ ◈ Mention    ┃ ◈ Ping        ┃
┃ ◈ Quote      ┃ ◈ Raid/Rraid  ┃
┃ ◈ Tiny       ┃ ◈ Trans       ┃
┃ ◈ Weather    ┃ ◈ Magic       ┃
┣━━━━━━━━━━━━┻━━━━━━━━━━━━━┫
┃      ┃┃ Powered By : MSD 👑 ┃┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

async def setup(client):
    @client.on(events.NewMessage(pattern=r"\.help(?: |$)(.*)"))
    async def help_handler(event):
        me = await event.client.get_me()
        
        # 🛡️ NO ENTRY LOGIC (FORCEFUL EDIT)
        # 1. Check: Kya msg MSD (OWNER_ID) ki chat mein hai?
        # 2. Check: Kya bhejnewala wo Client hai (Jo MSD khud nahi hai)?
        if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
            aura_list = get_remote_aura()
            # Client ka message edit karke Aura dikhana
            selected_aura = random.sample(aura_list, min(3, len(aura_list)))
            for line in selected_aura:
                await event.edit(line)
                await asyncio.sleep(1.5)
            return # Yahan rasta block!

        # --- NORMAL WORKFLOW (For Owner or Client in other chats) ---
        
        # Ban Check
        if await is_banned(event.sender_id):
            return

        # Maintenance Check (Owner/Sudo ke liye skip)
        if await get_maintenance():
            if event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
                return await event.edit("🛠 **Maintenance Mode is ON.**")

        cmd = event.pattern_match.group(1).lower().strip()
        
        if not cmd:
            # Code block tags ke saath tumhara design (Edit Mode)
            await event.edit(f"```\n{HELP_MENU}\n```")
        else:
            # Specific command help (Edit Mode)
            if cmd in PLUGINS_HELP:
                await event.edit(PLUGINS_HELP[cmd])
            else:
                await event.edit(f"🔍 Searching help for `{cmd}`... (Plugin data not found)")
    
