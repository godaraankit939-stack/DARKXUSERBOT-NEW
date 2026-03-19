import asyncio
from telethon import events
from telethon.tl.functions.messages import DeleteHistoryRequest

# Target AI Bot Username
TARGET_BOT = "@ChatGPT_General_Bot"

@events.register(events.NewMessage(pattern=r"\.ask ?(.*)"))
async def ask_ai(event):
    client = event.client
    query = event.pattern_match.group(1).strip()
    
    if not query:
        return await event.edit("`Syntax: .ask <your query>`")

    # Initial status message
    await event.edit("`🔍 Processing your request... Please wait.`")

    try:
        # Start a hidden conversation with a longer timeout (30s)
        async with client.conversation(TARGET_BOT, timeout=30) as conv:
            # Step 1: Initialize the bot
            await conv.send_message("/start")
            await asyncio.sleep(1) # Thoda extra gap taaki bot process kar sake
            
            # Step 2: Set Language (Only if necessary, can skip for speed)
            await conv.send_message("/language en")
            await asyncio.sleep(1)

            # Step 3: Send the User's query
            await conv.send_message(query)
            
            # Step 4: WAIT FOR RESPONSE (Sakt logic)
            # Ye line tab tak rukegi jab tak reply nahi aata
            response = await conv.get_response()
            answer = response.text

            # Response milne ke baad hi reply edit karega
            final_output = f"🤖 **AI Response:**\n\n{answer}\n\n**DARK-USERBOT 💀**"
            await event.edit(final_output)

        # ================= SMART CLEANUP SECTION =================
        # Response milne ke baad hi ye section trigger hoga
        await asyncio.sleep(2) # 2 sec ka gap taaki cleanup se pehle sync ho jaye
        entity = await client.get_input_entity(TARGET_BOT)
        
        # Deletes the entire history for both sides
        await client(DeleteHistoryRequest(
            peer=entity,
            max_id=0,
            just_clear=False, 
            revoke=True
        ))
        
        # Fully clears the dialog list
        await client.delete_dialog(TARGET_BOT)

    except asyncio.TimeoutError:
        await event.edit("`❌ Error: AI Bot took too long to respond. Try again later.`")
    except Exception as e:
        await event.edit(f"**Error:** `Failed to fetch response from AI.`\n`Log: {str(e)}` ")

async def setup(client):
    client.add_event_handler(ask_ai)
    
