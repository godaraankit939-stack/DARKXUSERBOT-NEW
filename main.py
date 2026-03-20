import os
import asyncio
import sys
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import (
    SessionPasswordNeededError, UserNotParticipantError
)

# --- IMPORT CONFIG & DB ---
import config
from database import (
    save_session, is_sudo, is_banned, 
    get_maintenance, get_all_sessions, get_sudo_list
)
from keep_alive import keep_alive

sys.path.append(os.getcwd())

# 𝖲𝖠𝖪𝖳𝖨: Render Port 8080 fix
try:
    keep_alive()
except:
    pass

# Client Initialize
bot = TelegramClient('manager_session', config.API_ID, config.API_HASH)

# --- FORCE JOIN CONFIG ---
AUTH_CHATS = ["dark_uploads", -1002341933066]
INVITE_LINKS = ["https://t.me/dark_uploads", "https://t.me/+Da6Oc_soDHA2YjE1"]

# --- 🛡️ SECURITY HELPERS ---

async def check_ban_and_maint(event):
    user_id = event.sender_id
    # 1. Ban Logic
    if await is_banned(user_id):
        if user_id == config.OWNER_ID: return False
        try:
            await event.reply("`YOU WERE BANNED BY OWNER!`")
            return True
        except: return True
    # 2. Maintenance Logic
    if await get_maintenance():
        if user_id == config.OWNER_ID or await is_sudo(user_id): return False
        try:
            await event.reply("🛠 **System Status: Maintenance Mode.**")
            return True
        except: return True
    return False

async def check_fjoin(user_id):
    for chat in AUTH_CHATS:
        try:
            await bot(GetParticipantRequest(channel=chat, participant=user_id))
        except UserNotParticipantError: return False
        except: continue
    return True

# ================= HANDLERS =================

# 1. START & VERIFY
@bot.on(events.NewMessage(pattern=r'^\/start$'))
async def start(event):
    if not event.is_private or await check_ban_and_maint(event): return
    if not await check_fjoin(event.sender_id):
        msg = "👑 **WELCOME TO DARK EMPIRE** 👑\n\nTO CONTINUE, JOIN THESE CHANNELS!"
        buttons = [
            [Button.url("📢 JOIN", INVITE_LINKS[0])],
            [Button.url("👥 JOIN", INVITE_LINKS[1])],
            [Button.inline("✅ Verify & Start", data="verify_join")]
        ]
        return await event.reply(msg, buttons=buttons)
    await event.reply(config.START_MSG)

@bot.on(events.CallbackQuery(data="verify_join"))
async def verify_callback(event):
    if await is_banned(event.sender_id) and event.sender_id != config.OWNER_ID:
        return await event.answer("❌ YOU ARE BANNED BY OWNER!", alert=True)
    if await check_fjoin(event.sender_id):
        await event.delete()
        await bot.send_message(event.sender_id, config.START_MSG)
    else:
        await event.answer("❌ JOIN BOTH FOR START!", alert=True)

# 2. ALIVE
@bot.on(events.NewMessage(pattern=r'^\/alive$'))
async def bot_alive(event):
    if await check_ban_and_maint(event): return
    await event.reply(config.ALIVE_TEXT)

# 3. HOSTING (OTP)
@bot.on(events.NewMessage(pattern=r'^\/host$'))
async def host_handler(event):
    if await check_ban_and_maint(event) or not await check_fjoin(event.sender_id): return
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("📲 **Send Phone Number (with Country Code).ex:+919067853456**")
        num_res = await conv.get_response()
        phone_number = num_res.text.replace(" ", "")
        status_msg = await conv.send_message("📨 **Sending OTP...**")
        client = TelegramClient(StringSession(), config.API_ID, config.API_HASH)
        await client.connect()
        try:
            await client.send_code_request(phone_number)
            await status_msg.edit("✅ **OTP Sent!**\nSend as: `1 2 3 4 5`")
        except Exception as e: return await status_msg.edit(f"❌ Error: `{e}`")
        otp_res = await conv.get_response()
        otp = otp_res.text.replace(" ", "")
        try:
            await client.sign_in(phone_number, otp)
        except SessionPasswordNeededError:
            await status_msg.edit("🔐 **2FA detected.** Send password:")
            pwd = await conv.get_response()
            await client.sign_in(password=pwd.text)
        except Exception as e: return await status_msg.edit(f"❌ Failed: `{e}`")
        session_str = client.session.save()
        user = await client.get_me()
        await save_session(user.id, session_str)
        await status_msg.delete()
        await conv.send_message(f"✅ **String:** `{session_str}`")
        await conv.send_message(config.LOGIN_SUCCESS)
        await client.disconnect()

# 4. CLONE (Manual String)
@bot.on(events.NewMessage(pattern=r'^\/clone ?(.*)'))
async def clone_handler(event):
    if await check_ban_and_maint(event): return
    string = event.pattern_match.group(1).strip()
    if not string: return await event.reply("`Usage: /clone <string_session>`")
    try:
        temp_client = TelegramClient(StringSession(string), config.API_ID, config.API_HASH)
        await temp_client.connect()
        me = await temp_client.get_me()
        await save_session(me.id, string)
        await temp_client.disconnect()
        await event.reply(f"✅ **Clone Successful!**\nUser: `{me.first_name}`")
    except Exception as e: await event.reply(f"❌ **Invalid String:** `{e}`")

# 5. PANEL
@bot.on(events.NewMessage(pattern=r'^\/panel$'))
async def panel_handler(event):
    if event.sender_id != config.OWNER_ID: return
    sessions, sudo_users = await get_all_sessions(), await get_sudo_list()
    maint_status = "ON 🚧" if await get_maintenance() else "OFF ✅"
    msg = f"💻 **DARK CONTROL PANEL**\n\n👤 Clones: `{len(sessions)}` \n🛡️ Sudo: `{len(sudo_users)}` \n🛠 Maint: `{maint_status}`"
    await event.reply(msg)

# ================= THE SAKT RUNNER =================
async def start_empire():
    # 1. Manager Bot Start
    await bot.start(bot_token=config.BOT_TOKEN)
    print("✅ Manager Bot Online!")

    # 2. Userbots/Clones Start (Ye missing tha)
    sessions = await get_all_sessions()
    for u_id, s_str in sessions.items():
        try:
            client = TelegramClient(StringSession(s_str), config.API_ID, config.API_HASH)
            await client.connect()
            # Yahan plugins load karne ka logic dalna hoga
            print(f"✅ Userbot {u_id} Started!")
        except: continue

    await bot.run_until_disconnected()
                                    

