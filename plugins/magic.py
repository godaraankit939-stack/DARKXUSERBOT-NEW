import asyncio
import random
import re
import requests
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

MAGIC = {"on": False}

# ================= AURA =================
def get_remote_aura():
    try:
        r = requests.get(AURA_URL, timeout=5)
        if r.status_code == 200:
            return [x.strip() for x in r.text.split("\n") if x.strip()]
    except:
        pass
    return ["ACCESS DENIED 🛡️"]

# ================= ITALIC CAPS FONT =================
FONT = {
    'A':'𝘈','B':'𝘉','C':'𝘊','D':'𝘋','E':'𝘌','F':'𝘍','G':'𝘎','H':'𝘏','I':'𝘐',
    'J':'𝘑','K':'𝘒','L':'𝘓','M':'𝘔','N':'𝘕','O':'𝘖','P':'𝘗','Q':'𝘘','R':'𝘙',
    'S':'𝘚','T':'𝘛','U':'𝘜','V':'𝘝','W':'𝘞','X':'𝘟','Y':'𝘠','Z':'𝘡'
}

# ================= EMOJI LOGIC =================
EMOJI = {
    "love":"❤️","hate":"🥀","king":"👑","raja":"👑","money":"💸","rich":"💰",
    "fire":"🔥","aag":"🔥","danger":"⚠️","dead":"💀","kill":"💀","war":"⚔️",
    "power":"⚡","strong":"💪","sad":"😢","happy":"😄","cool":"😎","boss":"💼",
    "time":"⏰","win":"🏆","loss":"📉","snake":"🐍","lion":"🦁","beast":"🦁",
    "dark":"🌑","light":"💡","god":"🔱","bhagwan":"🔱","error":"❌",
    "success":"✅","pro":"🌟","fast":"⚡","slow":"🐢","smart":"🧠",
    "beauty":"✨","hot":"🥵","cold":"❄️","broken":"💔","family":"🏡",
    "code":"💻","hacker":"👨‍💻","bot":"🤖","python":"🐍"
}

# ================= STYLE FUNCTION =================
def style_text(text):
    words = text.split()
    final = []

    for word in words:
        clean = re.sub(r'[^a-zA-Z]', '', word).lower()

        # uppercase force
        upper_word = word.upper()

        # font convert
        styled = ""
        for ch in upper_word:
            styled += FONT.get(ch, ch)

        # emoji add
        if clean in EMOJI:
            styled += EMOJI[clean]

        final.append(styled)

    return " ".join(final)

# ================= TOGGLE =================
@events.register(events.NewMessage(outgoing=True, pattern=r"\.magic$"))
async def toggle(event):
    if await is_banned(event.sender_id):
        return

    if await get_maintenance() and event.sender_id != OWNER_ID:
        return

    MAGIC["on"] = not MAGIC["on"]

    status = "ON 🔥" if MAGIC["on"] else "OFF ❌"
    await event.edit(f"`MAGIC MODE: {status}`")

    await asyncio.sleep(2)
    await event.delete()

# ================= AUTO MAGIC =================
@events.register(events.NewMessage(outgoing=True))
async def auto_magic(event):

    # security
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura = get_remote_aura()
        for line in random.sample(aura, min(3, len(aura))):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    if not MAGIC["on"]:
        return

    if event.text.startswith("."):
        return

    if await is_banned(event.sender_id):
        return

    original = event.text
    new = style_text(original)

    # IMPORTANT: avoid same text edit loop
    if original != new:
        try:
            await event.edit(new)
        except:
            pass

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(toggle)
    client.add_event_handler(auto_magic)
