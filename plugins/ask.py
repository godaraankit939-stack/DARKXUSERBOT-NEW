import asyncio
from telethon import events
from telethon.tl.functions.messages import DeleteHistoryRequest, DeleteChatUserRequest
from telethon.tl.functions.channels import LeaveChannelRequest

# Target AI Bot Username
TARGET_BOT = "@ChatGPT_General_Bot"

@events.register(events.NewMessage(pattern=r"\.ask ?(.*)"))
async def ask_ai(event):
    client = event.client
    query = event.pattern_match.group(1).strip()
    
    if not query:
        return await event.edit("`Syntax: .ask <your query>`")

    # Initial status message
    await event.edit("`Processing your request...`")

    try:
        # Start a hidden conversation with the target bot
        async with client.conversation(TARGET_BOT, timeout=15) as conv:
            # Step 1: Initialize the bot
            await conv.send_message("/start")
            await asyncio.sleep(0.5)
            
            # Step 2: Set Language to English
            await conv.send_message("/language en")
            await asyncio.sleep(0.5)

            # Step 3: Send the User's query
            await conv.send_message(query)
            
            # Step 4: Wait for the response
            response = await conv.get_response()
            answer = response.text

            # Final response to your original chat
            final_output = f"🤖 **AI Response:**\n\n{answer}\n\n**DARK-USERBOT 💀**"
            await event.edit(final_output)

        # ================= CLEANUP SECTION =================
        # This part completely deletes the chat history and removes the bot from your chat list
        entity = await client.get_input_entity(TARGET_BOT)
        
        # Deletes the entire history for both sides and removes from dialog list
        await client(DeleteHistoryRequest(
            peer=entity,
            max_id=0,
            just_clear=False, # Set to False to remove the dialog entirely
            revoke=True
        ))
        
        # Fully clears the dialog so it disappears from the chat list
        await client.delete_dialog(TARGET_BOT)

    except Exception as e:
        await event.edit(f"**Error:** `Failed to fetch response from AI.`\n`Log: {str(e)}` ")

async def setup(client):
    client.add_event_handler(ask_ai)
    
