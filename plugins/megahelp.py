import asyncio
from telethon import events
from database import get_maintenance, is_banned
from config import OWNER_ID

# --- THE EMPIRE HELP DATABASE ---
# Isme tu kabhi bhi nayi help add kar sakta hai niche format follow karke
HELP_DICT = {
    "raid": "⚔️ **RAID HELP**\n\n• `.raid [count] [@target/reply]` : Gaaliyo ki baarish.\n• `.sraid [count] [@target/reply]` : Shayri wala vaar.\n• `.rraid` : Ghost Hunter (Auto-Reply).\n• `.fsraid` : Stop all raids.",
    "spam": "🚀 **SPAM HELP**\n\n• `.spam [count] [text]` : Current chat spam.\n• `.dmspam [count] [@target] [text]` : Target ke DM mein spam.\n• `.fsspam` : Stop all spam.",
    "purge": "🧹 **PURGE HELP**\n\n• `.purge [count/reply]` : Chat saaf (Delete for All).\n• `.purgemy [count]` : Sirf apne purane msg delete karna.",
    "mention": "📢 **MENTION HELP**\n\n• `.mention @user [text]` : User mention with text.\n• `.tagall [text]` : Everyone 5x5 simple tag.\n• `.tagalle [text]` : Everyone 5x5 with Emojis.",
    "utility": "🛠️ **UTILITY HELP**\n\n• `.dic [A] [10]` : Dictionary spellings.\n• `.afk [reason]` : Away mode (Auto-Off on msg).\n• `.create [name]` : Create new GC.\n• `.info [@user]` : User details.",
    "magic": "🪄 **MAGIC HELP**\n\n• `.magic` : Toggle Mode (On/Off). Cool fonts + Emojis automatically.",
    "media": "🖼️ **MEDIA HELP**\n\n• `.tiny [reply]` : Shrink Photos/Stickers.\n• `.ss [reply]` : Save View-Once (Destruct) media.\n• `.quotly [reply]` : Text to Sticker.",
    "misc": "✨ **MISC HELP**\n\n• `.lyrics [song]` : Get lyrics.\n• `.meme` : Generate random meme.\n• `.clone [@user]` : Copy PFP/Name/Bio.",
    "sudo": "👑 **SUDO HELP**\n\n• `.sudo [reply/@user]` : Add Sudo.\n• `.rsudo [reply/@user]` : Remove Sudo.\n• `.sudos` : Show Sudo list."
}

# ================= 1. .specialhelp (Main Menu) =================
@events.register(events.NewMessage(pattern=r"\.specialhelp$"))
async def special_help(event):
    # 🛡️ NO-ENTRY LOGIC
    if event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        await event.edit("**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤▣** 🛡️")
        return

    help_msg = "👑 **MSD EMPIRE COMMAND CENTER** 👑\n\n"
    help_msg += "Use `.help [name]` for details:\n\n"
    help_msg += "`raid`, `spam`, `purge`, `mention`, `utility`, `magic`, `media`, `misc`, `sudo`"
    
    await event.edit(help_msg)

# ================= 2. .help [module] (Specific Details) =================
@events.register(events.NewMessage(pattern=r"\.help (.*)"))
async def individual_help(event):
    # 🛡️ NO-ENTRY LOGIC
    if event.chat_id == OWNER_ID and event.sender_id != OWNER_ID:
        await event.edit("**⌬ 𝖠𝖢𝖢𝖤𝖲𝖲 𝖣𝖤▵▨𝖤▣** 🛡️")
        return

    module = event.pattern_match.group(1).lower().strip()
    
    if module in HELP_DICT:
        await event.edit(HELP_DICT[module])
    else:
        await event.edit(f"❌ `{module}` naam ka koi module nahi hai lode!")
        await asyncio.sleep(2)
        await event.delete()

# ================= SETUP =================
async def setup(client):
    client.add_event_handler(special_help)
    client.add_event_handler(individual_help)
  
