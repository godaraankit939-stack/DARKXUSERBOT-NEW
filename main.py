import os
import asyncio
import sys
import glob
import importlib.util
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneNumberInvalidError, PhoneCodeInvalidError, UserNotParticipantError,
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError
)
from telethon.tl.functions.channels import GetParticipantRequest

# Config aur Database se functions uthana
from config import API_ID, API_HASH, BOT_TOKEN, START_MSG, LOGIN_SUCCESS, OWNER_ID
from database import (
    save_session, is_sudo, ban_user, unban_user, 
    is_banned, set_maintenance, get_maintenance,
    get_all_sessions, get_sudo_list
)

# Render fix: ensures config/database are found
sys.path.append(os.getcwd())

bot = TelegramClient('manager_session', API_ID, API_HASH)

# --- 🚀 NO ENTRY (FORCE JOIN) CONFIG ---
AUTH_CHATS = ["D4RK_ARMYY", "dark_uploads", -1002341933066] 
LINKS = [
    "https://t.me/dark_uploads",
    "https://t.me/+Da6Oc_soDHA2YjE1",
    "https://t.me/D4RK_ARMYY"
]
FJOIN_TEXT = "✨ **DARKXUSERBOT**\n\n**JOIN THESE CHANNELS TO CONTINUE 💫**"

# --- 🛠️ NO ENTRY HELPERS ---
async def is_joined(user_id):
    if user_id == OWNER_ID: return True
    for chat in AUTH_CHATS:
        try:
            await bot(GetParticipantRequest(channel=chat, participant=user_id))
        except UserNotParticipantError:
            return False
        except:
            continue
    return True

async def get_fjoin_buttons():
    return [
        [Button.url("📢 JOIN", LINKS[0])],
        [Button.url("📢 JOIN", LINKS[1])],
        [Button.url("📢 JOIN", LINKS[2])],
        [Button.inline("✅ VERIFY & START", data="verify")]
    ]

async def is_maint(user_id):
    if user_id == OWNER_ID or await is_sudo(user_id):
        return False
    return await get_maintenance()

# --- 📢 MANAGER BOT HANDLERS ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if await is_banned(event.sender_id):
        return await event.reply("❌ **You are banned from using this bot.**")
    if not await is_joined(event.sender_id):
        return await event.reply(FJOIN_TEXT, buttons=await get_fjoin_buttons())
    if await is_maint(event.sender_id):
        return await event.reply("🚧 **Bot is under Maintenance Mode.**")
    await event.reply(START_MSG, parse_mode='md')

@bot.on(events.CallbackQuery(data="verify"))
async def verify_cb(event):
    if await is_joined(event.sender_id):
        await event.delete()
        await bot.send_message(event.sender_id, START_MSG)
    else:
        await event.answer("❌ JOIN ALL CHANNELS! 🤡", alert=True)

@bot.on(events.NewMessage(pattern='/alive'))
async def bot_alive(event):
    if await is_banned(event.sender_id): return
    await event.reply("✨ **DARK MANAGER IS LIVE**\nStatus: `Running` 🚀")

# --- HOSTING & CLONE (As it is) ---
@bot.on(events.NewMessage(pattern='/host'))
async def host_handler(event):
    if await is_banned(event.sender_id): return
    if not await is_joined(event.sender_id):
        return await event.reply(FJOIN_TEXT, buttons=await get_fjoin_buttons())
    if await is_maint(event.sender_id): return await event.reply("🚧 Maintenance ON!")
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("📲 **Please send your Phone Number...**")
        number = await conv.get_response()
        phone_number = number.text.replace(" ", "")
        status_msg = await conv.send_message("📨 **Sending OTP...**")
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        try:
            await client.send_code_request(phone_number)
            await status_msg.edit("✅ **OTP Sent!**")
        except Exception as e:
            await status_msg.edit(f"❌ **Error:** `{e}`")
            return
        otp_res = await conv.get_response()
        otp = otp_res.text.replace(" ", "")
        try:
            await client.sign_in(phone_number, otp)
        except SessionPasswordNeededError:
            await status_msg.edit("🔐 **2FA detected.**")
            pwd = await conv.get_response()
            await client.sign_in(password=pwd.text)
        session_str = client.session.save()
        user_info = await client.get_me()
        await save_session(user_info.id, session_str)
        await status_msg.edit(f"✅ **Login Successful!**\n\n`{session_str}`")
        await client.disconnect()

@bot.on(events.NewMessage(pattern='/clone'))
async def clone_cmd(event):
    args = event.text.split(" ", 1)
    if len(args) < 2: return await event.reply("❌ **Usage:** `/clone <string_session>`")
    try:
        temp = TelegramClient(StringSession(args[1]), API_ID, API_HASH)
        await temp.connect()
        me = await temp.get_me()
        await save_session(me.id, args[1])
        await event.reply(f"✅ **Clone Successful!** {me.first_name}")
        await temp.disconnect()
    except Exception as e:
        await event.reply(f"❌ **Error:** `{e}`")

# --- ADMIN PANEL (As it is) ---
@bot.on(events.NewMessage(pattern='/ban'))
async def ban(event):
    if event.sender_id == OWNER_ID or await is_sudo(event.sender_id):
        reply = await event.get_reply_message()
        user_id = reply.sender_id if reply else int(event.text.split()[1])
        await ban_user(user_id)
        await event.reply(f"🚫 **User {user_id} Banned.**")

# --- 🚀 MULTI-USERBOT LOADING LOGIC (FIXED) ---
running_sessions = set()

async def starter(s_str):
    if s_str in running_sessions:
        return
    try:
        client = TelegramClient(StringSession(s_str), API_ID, API_HASH)
        await client.connect()
        if await client.is_user_authorized():
            running_sessions.add(s_str)
            me = await client.get_me()
            print(f"✅ Userbot Started for: {me.first_name}")

            # --- 🛡️ MASTER FILTER (Sakt Fix for AFK/Magic/Auto-TR) ---
            @client.on(events.NewMessage)
            async def master_filter(event):
                # AFK Fix: Agar message bahar se aaya hai, filter mat karo (return)
                if not event.out:
                    return 
                # Magic Fix: Agar message tumhara hai aur dot nahi hai, tab bhi bypass hone do
                if event.out and not event.text.startswith("."):
                    return

            # --- 🚀 PLUGINS LOADING ---
            plugin_files = glob.glob("plugins/*.py")
            for file in plugin_files:
                try:
                    module_name = f"plugins.{os.path.basename(file)[:-3]}"
                    spec = importlib.util.spec_from_file_location(module_name, file)
                    load_mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(load_mod)
                    if hasattr(load_mod, "setup"):
                        await load_mod.setup(client)
                except: continue
            
            await client.run_until_disconnected()
    except: pass
    finally:
        if s_str in running_sessions: running_sessions.remove(s_str)

async def auto_load_new_sessions():
    print("🔄 Dynamic Loader Active...")
    while True:
        try:
            sessions = await get_all_sessions()
            for s in sessions:
                s_str = s[1] if isinstance(s, (list, tuple)) else s
                asyncio.create_task(starter(s_str))
        except: pass
        await asyncio.sleep(5) # Railway ki stability ke liye 20s best hai
        
# --- MAIN RUNNER ---
async def run_everything():
    print("🛑✨ DARK-USERBOT Engine Starting...")
    await bot.start(bot_token=BOT_TOKEN)
    print("📢 Manager Bot is Online!")
    asyncio.create_task(auto_load_new_sessions())
    await bot.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_everything())
    except: pass
        
