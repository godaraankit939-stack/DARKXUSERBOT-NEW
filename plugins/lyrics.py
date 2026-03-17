import asyncio
import random
import requests
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID
import os

AURA_URL = "https://raw.githubusercontent.com/Ankit/DARK-USERBOT/main/auralines.txt"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_remote_aura():
    try:
        response = requests.get(AURA_URL, timeout=5)
        if response.status_code == 200:
            return [line.strip() for line in response.text.split('\n') if line.strip()]
    except:
        pass
    return ["**⌬ ACCESS DENIED 🛡️**"]


@events.register(events.NewMessage(pattern=r"\.lyrics ?(.*)"))
async def lyrics_handler(event):
    client = event.client
    me = await client.get_me()

    # OWNER PROTECTION
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        aura_list = get_remote_aura()
        for line in random.sample(aura_list, min(3, len(aura_list))):
            await event.edit(line)
            await asyncio.sleep(1.5)
        return

    if await is_banned(event.sender_id):
        return

    if await get_maintenance() and event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
        return await event.edit("`System Status: Maintenance Mode Active.`")

    if event.sender_id != me.id and not await is_sudo(event.sender_id):
        return await event.edit("`Not allowed.`")

    song_name = event.pattern_match.group(1).strip()
    if not song_name:
        return await event.edit("`Give song name...`")

    await event.edit(f"`🎵 Searching lyrics for: {song_name}...`")

    lyrics_text = None
    title = song_name.upper()
    artist = "Unknown Artist"

    # ================= API 1 (Lyrist) =================
    try:
        url = "https://lyrist.vercel.app/api/" + song_name.replace(" ", "%20")
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            data = res.json()
            if data.get("lyrics"):
                lyrics_text = data["lyrics"]
                title = data.get("title", title)
                artist = data.get("artist", artist)
    except:
        pass

    # ================= AI FALLBACK (OPENAI) =================
    if not lyrics_text and OPENAI_API_KEY:
        try:
            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{
                        "role": "user",
                        "content": f"Give full lyrics of the song: {song_name}"
                    }]
                },
                timeout=15
            )

            data = res.json()

            if "choices" in data:
                lyrics_text = data["choices"][0]["message"]["content"]

        except:
            pass

    # ================= AI FALLBACK (GEMINI) =================
    if not lyrics_text and GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

            res = requests.post(
                url,
                json={
                    "contents": [{
                        "parts": [{
                            "text": f"Give full lyrics of the song: {song_name}"
                        }]
                    }]
                },
                timeout=15
            )

            data = res.json()

            if "candidates" in data:
                lyrics_text = data["candidates"][0]["content"]["parts"][0]["text"]

        except:
            pass

    # ================= FINAL FAIL =================
    if not lyrics_text:
        return await event.edit("`Lyrics not found. Try another song.`")

    # FORMAT OUTPUT
    header = "╔══════════════════╗\n║  ❁ 𝖫𝖸𝖱𝖨𝖢𝖲 𝖥𝖮𝖴𝖭𝖣 ❁  ║\n╚══════════════════╝\n"
    meta = "**Song:** `" + str(title) + "`\n**Artist:** `" + str(artist) + "`\n\n"

    if len(lyrics_text) > 3500:
        lyrics_text = lyrics_text[:3500] + "\n... (Lyrics truncated)"

    code_block = "```\n" + str(lyrics_text) + "\n```"

    final_msg = header + meta + code_block + "\n\n**Powered By DARK-USERBOT 💀**"

    await event.edit(final_msg)


async def setup(client):
    client.add_event_handler(lyrics_handler)
