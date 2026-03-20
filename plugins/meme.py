import os
import random
import requests
import json
from telethon import events

# --- MEMORY SYSTEM (REPEAT PREVENT) ---
MEMORY_FILE = "meme_memory.json"
MAX_MEMORY = 500

def load_mem():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_mem(url):
    mem = load_mem()
    mem.append(url)
    if len(mem) > MAX_MEMORY:
        mem.pop(0)
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f)

# --- REDDIT FETCH LOGIC ---
SUBS = ["desimemes", "indiameme"]

async def fetch_media(mode="image"):
    """mode: image or video"""
    already_seen = load_mem()
    sub = random.choice(SUBS)
    # 50 memes ki request taaki filter kar sakein
    url = f"https://meme-api.com/gimme/{sub}/50"
    
    try:
        res = requests.get(url, timeout=10).json()
        all_memes = res.get("memes", [])
        
        # Filtering for Direct Media Links
        valid = []
        for m in all_memes:
            link = m['url'].lower()
            if link in already_seen:
                continue
            
            # 1. IMAGE FILTER (No GIFs, only JPG/PNG)
            if mode == "image":
                if link.endswith(('.jpg', '.jpeg', '.png')):
                    valid.append(m)
            
            # 2. VIDEO FILTER (Only Direct MP4/MKV)
            elif mode == "video":
                if link.endswith(('.mp4', '.mkv', '.mov')):
                    valid.append(m)

        if valid:
            # Hype logic: Most Upvoted pehle
            valid.sort(key=lambda x: x.get('ups', 0), reverse=True)
            chosen = valid[0]
            save_mem(chosen['url'])
            return chosen['url'], chosen['title']
            
    except: pass
    return None, None

# ================= COMMANDS =================

# --- .meme (Only Image) ---
@events.register(events.NewMessage(pattern=r"^\.meme$", outgoing=True))
async def meme_img(event):
    await event.edit("`📸 Fetching Desi Image...`")
    url, title = await fetch_media(mode="image")
    
    if url:
        try:
            await event.client.send_file(event.chat_id, url, caption=f"**{title}**")
            await event.delete()
        except:
            await event.edit("❌ Failed to send as Media. Link broken!")
    else:
        await event.edit("❌ No fresh image found in top 50.")

# --- .vmeme (Only Video) ---
@events.register(events.NewMessage(pattern=r"^\.vmeme$", outgoing=True))
async def meme_vid(event):
    await event.edit("`🎬 Fetching Hype Video...`")
    url, title = await fetch_media(mode="video")
    
    if url:
        try:
            # send_file automatically downloads the link and sends as Video
            await event.client.send_file(event.chat_id, url, caption=f"**{title}**")
            await event.delete()
        except:
            await event.edit("❌ Video link error or too large!")
    else:
        await event.edit("❌ No fresh video memes available right now.")

# ================= SETUP =================

async def setup(client):
    client.add_event_handler(meme_img)
    client.add_event_handler(meme_vid)
    print("✅ Strong Reddit Media Plugin Loaded!")
