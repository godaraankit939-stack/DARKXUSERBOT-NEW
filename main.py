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

# --- HOSTING & CLONE ---
@bot.on(events.NewMessage(pattern='/host'))
async def host_handler(event):
    if await is_banned(event.sender_id): return
    if not await is_joined(event.sender_id):
        return await event.reply(FJOIN_TEXT, buttons=await get_fjoin_buttons())
    if await is_maint(event.sender_id): return await event.reply("🚧 Maintenance ON!")
    
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("📲 **Please send your Phone Number with Country Code.**\nExample: `+919876543210`")
        number = await conv.get_response()
        phone_number = number.text.replace(" ", "")
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
            
        session_str = client.session.save()
        user_info = await client.get_me()
        user_id = user_info.id
        await save_session(user_id, session_str)
        
        await status_msg.edit(f"✅ **Login Successful!**\n\n**String Session:**\n`{session_str}`")
        await conv.send_message(f"{LOGIN_SUCCESS}\n\n**Save this string to auto login with /clone cmd**")
        await client.disconnect()

@bot.on(events.NewMessage(pattern='/clone'))
async def clone_cmd(event):
    if await is_banned(event.sender_id) or await is_maint(event.sender_id): return
    if not await is_joined(event.sender_id):
        return await event.reply(FJOIN_TEXT, buttons=await get_fjoin_buttons())
        
    args = event.text.split(" ", 1)
    if len(args) < 2:
        return await event.reply("❌ **Usage:** `/clone <string_session>`")
    
    status = await event.reply("⚙️ **Validating String Session...**")
    try:
        temp = TelegramClient(StringSession(args[1]), API_ID, API_HASH)
        await temp.connect()
        me = await temp.get_me()
        await save_session(me.id, args[1])
        await status.edit(f"✅ **Clone Successful!**\nWelcome **{me.first_name}**, your bot is live.")
        await temp.disconnect()
    except Exception as e:
        await status.edit(f"❌ **Invalid String:** `{e}`")

# --- 🛡️ ADMIN PANEL SECTION ---
@bot.on(events.NewMessage(pattern='/ban'))
async def ban(event):
    if event.sender_id == OWNER_ID or await is_sudo(event.sender_id):
        reply = await event.get_reply_message()
        args = event.text.split()
        user_id = reply.sender_id if reply else (int(args[1]) if len(args) > 1 else None)
        if user_id:
            if user_id == OWNER_ID: return await event.reply("Aura check! Owner cannot be banned.")
            await ban_user(user_id)
            await event.reply(f"🚫 **User {user_id} Banned.**")
        else:
            await event.reply("❌ **Reply to a user or provide ID.**")

@bot.on(events.NewMessage(pattern='/unban'))
async def unban_cmd(event):
    if event.sender_id == OWNER_ID or await is_sudo(event.sender_id):
        reply = await event.get_reply_message()
        args = event.text.split()
        user_id = reply.sender_id if reply else (int(args[1]) if len(args) > 1 else None)
        if user_id:
            await unban_user(user_id)
            await event.reply(f"✅ **User {user_id} Unbanned.**")
        else:
            await event.reply("❌ **Reply to a user or provide ID.**")

@bot.on(events.NewMessage(pattern='/maintenance'))
async def maint(event):
    if event.sender_id == OWNER_ID or await is_sudo(event.sender_id):
        curr = await get_maintenance()
        await set_maintenance(not curr)
        status = "ON 🛠" if not curr else "OFF ✅"
        await event.reply(f"🚧 **Maintenance Mode is now {status}**")

@bot.on(events.NewMessage(pattern='/panel'))
async def panel(event):
    if event.sender_id == OWNER_ID:
        sessions = await get_all_sessions()
        sudo_list = await get_sudo_list()
        maint_status = "ON 🛠" if await get_maintenance() else "OFF ✅"
        msg = (
            "📊 **DARK-USERBOT ADMIN PANEL**\n\n"
            f"🚀 **Active Userbots:** `{len(sessions)}`\n"
            f"🛡 **Sudo Users:** `{len(sudo_list)}`\n"
            f"🚧 **Maintenance:** `{maint_status}`\n"
            f"👤 **Owner ID:** `{OWNER_ID}`"
        )
        await event.reply(msg)

# --- 🚀 MULTI-USERBOT LOADING LOGIC ---
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

            # --- 🛡️ MASTER FILTER (Double Response Fix) ---
            @client.on(events.NewMessage)
            async def master_filter(event):
                # FIXED: Check karo ki message bhejnewala wahi client hai ya nahi
                me_id = (await client.get_me()).id
                if event.sender_id != me_id:
                    if not event.out:
                        return 
                    raise events.StopPropagation

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
        await asyncio.sleep(20)
        
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
        
