from telethon import events
import asyncio

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.test$"))
async def test_handler(event):
    await event.edit("✅ Animation Plugin Loaded & Working!")
    
