import os
import asyncio
import sys
import glob
import importlib.util
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
    is_banned, set_maintenance, get_maintenance,
    get_all_sessions, get_sudo_list
)
# --- KEEP ALIVE IMPORT ---
from keep_alive import keep_alive

# Render fix: ensures config/database are found
sys.path.append(os.getcwd())

# 𝖲𝖠𝖪𝖳𝖨: Render ko zinda rakhne ke liye server start
keep_alive()

# Bot Client Initialize - Manager Bot
bot = TelegramClient('manager_session', API_ID, API_HASH)

# --- MAINTENANCE CHECK HELPER ---
async def is_maint(user_id):
    if user_id == OWNER_ID or await is_sudo(user_id):
        return False
    return await get_maintenance()

# --- MANAGER BOT HANDLERS ---

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    # Ban check logic
    if await is_banned(event.sender_id):
        return await event.reply("❌ **You are banned from using this bot.**")
    # Maintenance check logic
    if await is_maint(event.sender_id):
        return await event.reply("🚧 **Bot is under Maintenance Mode.**")
    await event.reply(START_MSG, parse_mode='md')

@bot.on(events.NewMessage(pattern='/alive'))
async def bot_alive(event):
    if await is_banned(event.sender_id): return
    await event.reply("✨ **DARK MANAGER IS LIVE**\nStatus: `Running` 🚀")

# --- HOSTING LOGIC (OTP/LOGIN) ---
@bot.on(events.NewMessage(pattern='/host'))
async def host_handler(event):
    if await is_banned(event.sender_id): return
    if await is_maint(event.sender_id): return await event.reply("🚧 Maintenance ON!")
    
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("📲 **Please send your Phone Number with Country Code.**\nExample: `+919876543210`")
        
        number = await conv.get_response()
        phone_number = number.text.replace(" ", "")
        
        # OTP Status Update
        status_msg = await conv.send_message("📨 **Sending OTP... Please wait.**")
        
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        
        try:
            await client.send_code_request(phone_number)
            await status_msg.edit("✅ **OTP Sent!**\nPlease send it like: `1 2 3 4 5` (With spaces)")
        except Exception as e:
            await status_msg.edit(f"❌ **Error:** `{e}`")
            return

        otp_res = await conv.get_response()
        otp = otp_res.text.replace(" ", "")

        # Login Status Update
        await status_msg.edit("⚙️ **Logging in... Please wait.**")

        try:
            await client.sign_in(phone_number, otp)
        except SessionPasswordNeededError:
            await status_msg.edit("🔐 **2FA detected.** Send your password:")
            pwd = await conv.get_response()
            try:
                await client.sign_in(password=pwd.text)
            except:
                await status_msg.edit("❌ **Wrong Password.**")
                return
        except Exception as e:
            await status_msg.edit(f"❌ **Login Failed:** `{e}`")
            return

        # Success - Session Store
        session_str = client.session.save()
        user_info = await client.get_me()
        user_id = user_info.id
        await save_session(user_id, session_str)
        
        await status_msg.edit(f"✅ **Login Successful!**\n\n**String Session:**\n`{session_str}`")
        await conv.send_message(LOGIN_SUCCESS)
        await client.disconnect()

# --- CLONE COMMAND (String Support) ---
@bot.on(events
        
