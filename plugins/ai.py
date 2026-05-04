import asyncio
from telethon import events
from g4f.client import Client

# AI Client initialize
ai_client = Client()

# RAM-based storage (Restart pe reset ho jayega)
# Agar permanent chahiye toh Database use kar sakte hain
AI_CHATS = set()

async def get_ai_response(text):
    try:
        # GPT-3.5/4 ka free access via g4f
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ **AI Error:** `{str(e)}`"

async def setup(client):
    # --- TOGGLE COMMAND ---
    @client.on(events.NewMessage(pattern=r"\.ai$", outgoing=True))
    async def toggle_ai(event):
        chat_id = event.chat_id
        if chat_id in AI_CHATS:
            AI_CHATS.remove(chat_id)
            await event.edit("🤖 **Auto AI: DEACTIVATED** in this chat.")
        else:
            AI_CHATS.add(chat_id)
            await event.edit("🤖 **Auto AI: ACTIVATED** in this chat.")

    # --- AUTO RESPONSE LOGIC ---
    @client.on(events.NewMessage(incoming=True))
    async def auto_ai_reply(event):
        # Conditions check:
        # 1. Chat mein AI on honi chahiye
        # 2. Bot khud ke messages pe reply na kare
        # 3. Message khali na ho
        if event.chat_id not in AI_CHATS:
            return
        if event.is_bot or event.is_group: # Groups mein kalesh na ho isliye sirf PM (Optional)
            return
        if not event.text or event.text.startswith("."):
            return

        # Typing action for realism
        async with event.client.action(event.chat_id, 'typing'):
            response = await get_ai_response(event.text)
            if response:
                await event.reply(response)

# --- INFO ---
# .ai command se on-off hoga.
# Jis chat mein on karoge, wahan bot samne wale ke har msg ka jawab dega.
