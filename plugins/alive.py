import time
from telethon import events
from database import get_maintenance, is_sudo
from config import OWNER_ID

# Final Minimalist Alive Design jo humne finalize kiya tha
ALIVE_TEXT = (
    "**⌬ 𝖣𝖠𝖱𝖪-𝖴𝖲𝖤𝖱𝖡𝖮𝖳 𝖨𝖲 𝖠𝖫𝖨𝖵𝖤 ⚡**\n\n"
    "◈ **𝖵𝖾𝗋𝗌𝗂𝗈𝗇:** `𝟩.𝟢 (𝖳𝗁𝖺𝗅𝖺 𝖥𝗈r 𝖠 𝖱𝖾𝖺𝗌𝗈𝗇)`\n"
    "◈ **𝖲𝗍𝖺𝗍𝗎𝗌:** `𝖱𝖾𝖺𝖽𝗒 𝗍𝗈 𝖣𝖾𝗌𝗍𝗋𝗈𝗒` 💀"
)

async def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.alive"))
    async def alive_handler(event):
        # --- MAINTENANCE CHECK ---
        if await get_maintenance():
            # Owner aur Sudo ko maintenance affect nahi karegi
            if event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
                return await event.edit("🛠 **DARK-USERBOT is currently under Maintenance.**")

        # Final Message Edit
        await event.edit(ALIVE_TEXT)
      
