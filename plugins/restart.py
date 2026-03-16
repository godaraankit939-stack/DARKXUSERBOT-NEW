import os
import sys
import asyncio
from telethon import events
from database import get_maintenance, is_sudo, is_banned
from config import OWNER_ID

async def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.restart"))
    async def restart_handler(event):
        # 1. BAN CHECK
        if await is_banned(event.sender_id):
            return

        # 2. MAINTENANCE CHECK
        if await get_maintenance():
            if event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
                return await event.edit("🛠 **Maintenance Mode is ON.**")

        # Restarting Logic
        await event.edit("`Restarting DARK-USERBOT...` 🔄\n`Please wait for a moment.`")
        
        # Connection band karke process restart karna
        await client.disconnect()
        
        # Python interpreter ko dobara call karna same arguments ke saath
        os.execl(sys.executable, sys.executable, *sys.argv)

