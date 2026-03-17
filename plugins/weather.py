import asyncio
import random
import requests
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

# --- CONFIG ---
AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

def get_remote_aura():
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except Exception:
        pass
    return ["**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤𝖣** 🛡️"]

# ================= WEATHER CMD (WTTR.IN LOGIC) =================
@events.register(events.NewMessage(pattern=r"\.weather ?(.*)"))
async def weather_search(event):
    client = event.client

    # 🛡️ 1. NO ENTRY LOGIC (Exact working logic from history)
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        selected_aura = random.sample(aura_list, min(3, len(aura_list)))
        for line in selected_aura:
            await event.edit(line)
            await asyncio.sleep(1.5) 
        return

    # 🛠️ 2. BAN & MAINTENANCE & SUDO CHECK
    if await is_banned(event.sender_id):
        return
    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode Active.`")

    place = event.pattern_match.group(1).strip()
    if not place:
        return await event.edit("`Error: City name ya Pincode toh do?`")

    await event.edit(f"`☁️ Scanning Atmosphere: {place}...`")

    try:
        # 🚀 WTTR.IN LOGIC: Faster & No Key Required
        # format: %l (location), %C (condition), %t (temp), %h (humidity), %w (wind)
        url = f"https://wttr.in/{place}?format=%l:+%C+%t+%h+%w"
        res = requests.get(url, timeout=10).text

        if "Unknown location" in res or "404" in res:
            return await event.edit("`❌ Error: Location not found.`")

        # 📋 Point-to-Point Clean Result
        # wttr.in se direct format milta hai, hum use bas header-footer de rahe hain
        weather_res = (
            f"☁️ **Weather Report:**\n\n"
            f"`{res}`\n\n"
            f"**DARK-USERBOT** 💀"
        )
        await event.edit(weather_res)

    except Exception as e:
        await event.edit(f"`❌ Error: Server busy or {str(e)}`")


# ================= SETUP =================
async def setup(client):
    client.add_event_handler(weather_search)
        
