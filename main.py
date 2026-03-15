import os, asyncio
import sys
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneNumberInvalidError, PhoneCodeInvalidError, 
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError
)
# Config aur Database se functions uthana
from config import API_ID, API_HASH, BOT_TOKEN, START_MSG, LOGIN_SUCCESS, OWNER_ID
from database import (
    save_session, is_sudo, ban_user, unban_user, 
    is_banned, set_maintenance, get_maintenance
)

# Render fix: ensures config/database are found
sys.path.append(os.getcwd())

# Bot Client Initialize (Global define, but start inside loop)
bot = TelegramClient('manager_bot', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    # Ban check
    if await is_banned(event.sender_id):
        return await event.reply("❌ **You are banned from using this bot.**")
    await event.reply(START_MSG, parse_mode='md')

@bot.on(events.NewMessage(pattern='/alive'))
async def bot_alive(event):
    await event.reply("✨ **DARK MANAGER IS LIVE**\nStatus: `Running` 🚀")

# --- HOSTING LOGIC (OTP/LOGIN) ---
@bot.on(events.NewMessage(pattern='/host'))
async def host_handler(event):
    if await is_banned(event.sender_id): return
    
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("📲 **Please send your Phone Number with Country Code.**\nExample: `+919876543210`")
        
        number = await conv.get_response()
        phone_number = number.text.replace(" ", "")
        
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        
        try:
            await client.send_code_request(phone_number)
        except PhoneNumberInvalidError:
            await conv.send_message("❌ **Invalid Phone Number.** Restart /host.")
            return

        await conv.send_message("📩 **OTP sent to your Telegram.**\nPlease send it like: `1 2 3 4 5`")
        otp_res = await conv.get_response()
        otp = otp_res.text.replace(" ", "")

        try:
            await client.sign_in(phone_number, otp)
        except SessionPasswordNeededError:
            await conv.send_message("🔐 **2FA detected.** Send your password:")
            pwd = await conv.get_response()
            try:
                await client.sign_in(password=pwd.text)
            except:
                await conv.send_message("❌ **Wrong Password.**")
                return
        except Exception:
            await conv.send_message("❌ **Login Failed.**")
            return

        session_str = client.session.save()
        user_id = (await client.get_me()).id
        await save_session(user_id, session_str)
        await conv.send_message(LOGIN_SUCCESS)
        await client.disconnect()

# --- HIDDEN ADMIN COMMANDS ---
@bot.on(events.NewMessage(pattern='/ban'))
async def ban(event):
    if event.sender_id == OWNER_ID or await is_sudo(event.sender_id):
        reply = await event.get_reply_message()
        user_id = reply.sender_id if reply else None
        if user_id:
            if user_id == OWNER_ID: return await event.reply("Aura check! Owner cannot be banned.")
            await ban_user(user_id)
            await event.reply(f"🚫 **User {user_id} Banned.**")

@bot.on(events.NewMessage(pattern='/maintenance'))
async def maint(event):
    if event.sender_id == OWNER_ID or await is_sudo(event.sender_id):
        curr = await get_maintenance()
        await set_maintenance(not curr)
        await event.reply(f"🚧 **Maintenance:** {'ON' if not curr else 'OFF'}")

# --- ASYNC LOOP FIX (Render special) ---
async def run_manager():
    # Bot ko async context ke andar start kar rahe hain
    await bot.start(bot_token=BOT_TOKEN)
    print("Manager Bot Started...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    # Naya loop create karke bot start karna
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_manager())
    except KeyboardInterrupt:
        pass
        
