import asyncio
import random
from telethon import events
from database import get_maintenance, is_banned, is_sudo
from config import OWNER_ID

# --- THE COMPLETE EMPIRE DATABASE ---
HELP_DICT = {
    "raid": "⚔️ **RAID HELP**\n• `.raid [count] [target]`\n• `.sraid [count] [target]`\n• `.rraid` (Reply to start)\n• `.drraid` (Stop RRAID)\n• `.fsraid` (Kill loops)",
    "spam": "🚀 **SPAM HELP**\n• `.spam [count] [text]`\n• `.dmspam [count] [target] [text]`\n• `.fsspam` (Force stop)",
    "purge": "🧹 **PURGE HELP**\n• `.purge [reply]` (All from here)\n• `.purge [count]` (Mix delete)\n• `.purge [count] [reply]` (Upward count)\n• `.purgemy [count]` (Only your msgs)",
    "sudo": "👑 **SUDO HELP**\n• `.sudo [reply/@user]` : Add\n• `.rsudo [reply/@user]` : Remove\n• `.sudos` : Show Empire List",
    "antipm": "🚫 **ANTIPM HELP**\n• `.antipm on/off` : Block/Allow unknown DMs.",
    "mention": "📢 **MENTION HELP**\n• `.mention @user [text]` : Custom mention.\n• `.tagall [text]` : 5x5 Simple tag.\n• `.tagalle [text]` : 5x5 Emoji tag.",
    "tiny": "🖼️ **TINY HELP**\n• `.tiny [reply]` : Shrink Photos/Stickers to 200px (Normal Image).",
    "destruct": "🛡️ **DESTRUCT HELP**\n• `.ss [reply]` : Save View-Once/Destructing media permanently.",
    "quotly": "💬 **QUOTLY HELP**\n• `.quotly [reply]` : Message to Sticker.",
    "clone": "👤 **CLONE HELP**\n• `.clone [@user/reply]` : Copy Name, Bio, and PFP.",
    "create": "🏗️ **CREATE HELP**\n• `.create [gc name]` : Create a new Group Chat.",
    "ask": "🔍 **Ask HELP **\n• `.ask [query/ask something]` : Ai/google help.",
    "magic": "🪄 **MAGIC HELP**\n• `.magic` : Toggle Mode. Auto-convert text to Cool Fonts + Emojis.",
    "autotr": "🌍 **AUTO-TR HELP**\n• `.autotr [lang]` : Real-time ghost translation edit. `.autotr` to OFF.",
    "dict": "📖 **DICTIONARY HELP**\n• `.dic [A] [limit]` : List spellings starting with alphabet.",
    "afk": "💤 **AFK HELP**\n• `.afk [reason/optional]` : Away mode. Auto-off on your next message.",
    "info": "ℹ️ **INFO HELP**\n• `.info [@user/reply]` : Get ID, Name, DC, and Profile details.",
    "b-cast": "ℹ️ **Broadcast HELP**\n• `.bcast [msg/reply to msg]` :Forward msg in one click to all chats.",
    "flirt": "ℹ️ **Flirt HELP**\n• `.flirt [@user/reply]` : To flirt with user.",
    "Animate": "ℹ️ **ANIMATION HELP**\n• `.animation` : To know the list of all animation.",
    "ping": "⚡ **PING HELP**\n• `.ping` : Check bot speed/latency.",
    "alive": "👑 **ALIVE HELP**\n• `.alive` : Check if bot is working + System Info.",
    "lyrics": "🎵 **LYRICS HELP**\n• `.lyrics [song name]` : Find full song lyrics.",
    "memify": "🤡 **MEME HELP**\n• `.meme` : Generate instant random memes.",
    "hot": "ℹ️ **HOT HELP**\n• `.hot [18+ SPAM]` : P*rn spam.",
    "tiny_text": "📐 **TINY TEXT**\n• `.tiny [text]` : Convert text to tiny fonts.",
    "translate": "㊙️ **TRANSLATE**\n• `.tr [reply to msg]` : Manual translation.",
    "weather": "🌦️ **WEATHER**\n• `.weather [city]` : Get weather info.",
    "song": "🎧 **SONG**\n• `.song [name]` : Download/Find song.",
    "restart": "🔄 **RESTART**\n• `.restart` : Reboot the userbot."
}


ALIASES = {
    "sraid": "raid", "rraid": "raid", "drraid": "raid", "fsraid": "raid",
    "dmspam": "spam", "fsspam": "spam",
    "purgemy": "purge",
    "tagall": "mention", "tagalle": "mention",
    "rsudo": "sudo", "sudos": "sudo",
    "tr": "translate"
}

# ================= 1. .specialhelp =================
@events.register(events.NewMessage(pattern=r"^\.specialhelp$"))
async def special_help(event):
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        await event.edit("**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤▣** 🛡️")
        return
    if await is_banned(event.sender_id):
        return
    
    msg = "👑 **MSD EMPIRE MEGA HELP** 👑\n\n"
    msg += "Type `.help [command]` for details:\n\n"
    msg += "⚔️ `raid`, `spam`, `purge`, `mention`\n"
    msg += "🛠️ `sudo`, `tiny`, `ss`, `magic`, `autotr`\n"
    msg += "✨ `afk`, `dic`, `clone`, `quotly`, `info`, `lyrics`\n"
    msg += "⚙️ `ping`, `alive`, `create`, `meme`, `antipm`"
    
    try:
        await event.edit(msg)
    except:
        await event.reply(msg)

# ================= 2. .help [command] =================
# Pattern changed to r"^\.help\s+(.+)" (Requires a space and a word)
@events.register(events.NewMessage(pattern=r"^\.help\s+(.+)"))
async def individual_help(event):
    # 🛡️ 1. SECURITY CHECKS (OWNER/BAN CHECK)
    if event.is_private and event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        return

    if await is_banned(event.sender_id):
        return

    cmd = event.pattern_match.group(1).lower().strip()
    target = ALIASES.get(cmd, cmd)
    
    if target in HELP_DICT:
        # Code block hata diya, ab seedha HELP_DICT ka text jayega (Bold/Markdown)
        try:
            # Edit mode for Owner/Sudo
            await event.edit(HELP_DICT[target])
        except:
            # Reply mode for Public users
            await event.reply(HELP_DICT[target])
    else:
        # Agar command nahi mili toh error message
        err_msg = f"❌ `{cmd}` NO PLUGIN FOUND!"
        try:
            await event.edit(err_msg)
            await asyncio.sleep(2)
            await event.delete()
        except:
            reply = await event.reply(err_msg)
            await asyncio.sleep(2)
            await reply.delete()

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(special_help)
    client.add_event_handler(individual_help)
    
    
