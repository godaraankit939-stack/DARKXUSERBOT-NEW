import asyncio
import random
import requests
from datetime import datetime
from telethon import events, functions, types
from telethon.tl.functions.users import GetFullUserRequest
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- GITHUB CONFIG (Aura Lines) ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

def get_remote_aura():
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

# --- UPDATED ACCOUNT AGE LOGIC (2026 Updated) ---
def get_account_age(user_id):
    if user_id < 100000000: return "10-12 Years (Ancient)"
    if user_id < 500000000: return "8-10 Years"
    if user_id < 1000000000: return "6-7 Years"
    if user_id < 2000000000: return "4-5 Years"
    if user_id < 4000000000: return "2-3 Years"
    if user_id < 6000000000: return "1-2 Years"
    if user_id < 7500000000: return "Less than 1 Year"
    return "Freshly Created (New)"

@events.register(events.NewMessage(pattern=r"\.info ?(.*)"))
async def user_info(event):
    client = event.client
    me = await client.get_me()

    # 🛡️ 1. NO ENTRY LOGIC
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        for line in random.sample(aura_list, min(3, len(aura_list))):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    # 🛠️ 2. BAN & MAINTENANCE CHECK
    if await is_banned(event.sender_id): return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`Status: Maintenance Mode Active.`")

    input_str = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    
    await event.edit("`🔍 Scanning User Intelligence...`")

    try:
        if reply:
            user = await client.get_entity(reply.sender_id)
        elif input_str:
            user = await client.get_entity(input_str)
        else:
            user = me

        full_user = await client(GetFullUserRequest(user.id))
        
        # Core Details
        u_id = user.id
        first_name = user.first_name
        last_name = user.last_name or ""
        username = f"@{user.username}" if user.username else "None"
        dc_id = getattr(user.photo, 'dc_id', "Unknown") if user.photo else "No PFP"
        bio = full_user.full_user.about or "No Bio Provided"
        common_chats = full_user.full_user.common_chats_count
        
        # Premium & Verification Check
        is_premium = "Yes 💎" if getattr(user, 'premium', False) else "No"
        is_bot = "Yes 🤖" if user.bot else "No"
        is_verified = "Verified ✅" if getattr(user, 'verified', False) else "No"
        is_scam = "Yes 🚫" if getattr(user, 'scam', False) else "Clean"
        
        # History & Age
        acc_age = get_account_age(u_id)
        
        # Constructing Detailed Report
        info_msg = (
            f"👤 **USER INTELLIGENCE REPORT**\n\n"
            f"◈ **Full Name:** `{first_name} {last_name}`\n"
            f"◈ **User ID:** `{u_id}`\n"
            f"◈ **Username:** {username}\n"
            f"◈ **Premium:** `{is_premium}`\n"
            f"◈ **Verified:** `{is_verified}`\n"
            f"◈ **Data Center:** `DC-{dc_id}`\n"
            f"◈ **Account Age:** `{acc_age}`\n\n"
            f"◈ **Bot:** `{is_bot}` | **Scam:** `{is_scam}`\n"
            f"◈ **Common Groups:** `{common_chats}`\n\n"
            f"◈ **Bio:** `{bio}`\n\n"
            f"**Powered By DARK-USERBOT** 💀"
        )
        
        await event.edit(info_msg)

    except Exception as e:
        await event.edit(f"❌ **Intelligence Failure:** `{str(e)}`")

# --- SETUP FUNCTION ---
async def setup(client):
    client.add_event_handler(user_info)
    
