import random
import requests
from telethon import events

# ================== CONFIG ==================

TENOR_API_KEY = "LIVDSRZULELA"

SEARCH_TERMS = [
    "indian meme",
    "babu rao meme",
    "bollywood reaction meme",
    "carryminati meme",
    "akshay kumar meme",
    "rajpal yadav meme"
]

REDDIT_SUBS = [
    "IndianDankMemes",
    "dankinindia",
    "memes"
]

# 👉 Telegram channels (public only)
TG_CHANNELS = [
    "indianmemes",
    "desimemes",
    "bollywoodmemes"
]

# ================== TENOR ==================

def get_tenor_meme():
    try:
        query = random.choice(SEARCH_TERMS)
        url = f"https://g.tenor.com/v1/search?q={query}&key={TENOR_API_KEY}&limit=20"
        
        res = requests.get(url).json()
        results = res.get("results", [])
        
        if results:
            gif = random.choice(results)
            return gif["media"][0]["gif"]["url"]
    except:
        pass
    return None

# ================== REDDIT ==================

def get_reddit_meme():
    try:
        sub = random.choice(REDDIT_SUBS)
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit=50"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers).json()
        
        posts = res["data"]["children"]
        memes = []

        for p in posts:
            url = p["data"]["url"]
            if url.endswith((".jpg", ".png", ".jpeg", ".gif")):
                memes.append(url)

        if memes:
            return random.choice(memes)
    except:
        pass
    return None

# ================== TELEGRAM ==================

async def get_telegram_meme(client):
    try:
        channel = random.choice(TG_CHANNELS)
        msgs = await client.get_messages(channel, limit=20)

        media_msgs = [m for m in msgs if m.media]

        if media_msgs:
            return random.choice(media_msgs)
    except:
        pass
    return None

# ================== COMMANDS ==================

# 🔥 MIXED AUTO MEME
@events.register(events.NewMessage(pattern=r"\.meme"))
async def meme(event):
    await event.edit("`😂 Fetching Meme...`")

    choice = random.choice(["tenor", "reddit", "telegram"])

    if choice == "tenor":
        meme = get_tenor_meme()
        if meme:
            await event.delete()
            return await event.client.send_file(event.chat_id, meme)

    elif choice == "reddit":
        meme = get_reddit_meme()
        if meme:
            await event.delete()
            return await event.client.send_file(event.chat_id, meme)

    else:
        msg = await get_telegram_meme(event.client)
        if msg:
            await event.delete()
            return await msg.forward_to(event.chat_id)

    await event.edit("❌ No meme found")

# 📦 TELEGRAM MEMES ONLY
@events.register(events.NewMessage(pattern=r"\.tmeme"))
async def tmeme(event):
    await event.edit("`📦 Fetching Telegram Meme...`")

    msg = await get_telegram_meme(event.client)
    if msg:
        await event.delete()
        return await msg.forward_to(event.chat_id)

    await event.edit("❌ No Telegram meme found")

# 😂 REDDIT MEMES ONLY
@events.register(events.NewMessage(pattern=r"\.rmeme"))
async def rmeme(event):
    await event.edit("`🔥 Fetching Reddit Meme...`")

    meme = get_reddit_meme()
    if meme:
        await event.delete()
        return await event.client.send_file(event.chat_id, meme)

    await event.edit("❌ No Reddit meme found")

# ================== SETUP ==================

async def setup(client):
    client.add_event_handler(meme)
    client.add_event_handler(tmeme)
    client.add_event_handler(rmeme)
