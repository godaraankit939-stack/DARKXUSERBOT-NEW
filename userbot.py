import asyncio
import importlib
import os
import sys
from pathlib import Path
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Environment aur Database se imports
from config import API_ID, API_HASH, OWNER_ID
from database import get_all_sessions, get_maintenance, is_sudo

# Render fix: ensures config/database are found
sys.path.append(os.getcwd())

async def start_userbots():
    """Database se saare sessions uthakar ek saath start karne ke liye"""
    sessions = await get_all_sessions()
    
    if not sessions:
        print("ℹ️ No hosted sessions found in Database.")
        return

    print(f"🔥 Starting {len(sessions)} Userbots... Please wait.")

    for session_str in sessions:
        try:
            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            # await client.connect() ki jagah seedha start() loop ke andar safe hai
            await client.start()

            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"✅ Live: {me.first_name} (@{me.username})")

                # --- GLOBAL MAINTENANCE HANDLER ---
                @client.on(events.NewMessage(outgoing=True))
                async def global_maintenance_manager(event):
                    if await get_maintenance():
                        # Owner aur Sudo ko maintenance affect nahi karegi
                        if event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
                            if event.text.startswith("."):
                                await event.edit("🛠 **DARK-USERBOT is currently under Maintenance.**\nCommands are disabled for now.")
                                # Agle plugins ko execute hone se rokne ke liye
                                raise events.StopPropagation

                # --- DYNAMIC PLUGIN LOADER ---
                await load_plugins(client)
                
                # Client ko background task mein run karna
                asyncio.create_task(client.run_until_disconnected())
            
            else:
                print(f"❌ Session invalid or expired: {session_str[:15]}...")

        except Exception as e:
            print(f"⚠️ Failed to start a session: {e}")

async def load_plugins(client):
    """Plugins load karne ka logic"""
    path = Path("plugins")
    if not path.exists():
        os.makedirs(path)
        
    for file in path.glob("*.py"):
        if file.name == "__init__.py":
            continue
        
        module_path = f"plugins.{file.stem}"
        try:
            # Module ko reload/import karna
            plugin = importlib.import_module(module_path)
            
            # Har plugin mein setup(client) function hona chahiye
            if hasattr(plugin, "setup"):
                await plugin.setup(client)
        except Exception as e:
            print(f"❗ Error loading plugin {file.name}: {e}")

if __name__ == "__main__":
    print("🛑✨ DARK-USERBOT Engine Starting...")
    # New event loop setup to fix RuntimeError on Render
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_userbots())
        print("🚀 All hosted accounts are now active.")
        loop.run_forever()
    except KeyboardInterrupt:
        print("🛑 Engine Stopped.")
        
