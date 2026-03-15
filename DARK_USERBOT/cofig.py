import os

# --- API KEYS (Render Environment Variables se uthayenge) ---
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URL = os.getenv("MONGO_URL", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# --- STYLISH MESSAGES (Jo tumne provide kiye) ---
START_MSG = """
`+----------------------------+`
`|  ❁ 𝖣𝖠𝖱𝖪 𝖴𝖲𝖤𝖱𝖡𝖮𝖳 𝖮𝖭𝖫𝖨𝖭𝖤 ❁ |`
`+----------------------------+`
`|  Welcome to the Power Hub  |`
`|  Developer: Ankit          |`
`|  Support: @WILDxMSD        |`
`+----------------------------+`

**𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:**
⚡ `/host` - Login via OTP
⚡ `/clone` - Login via String
⚡ `/alive` - Check Bot Status
"""

LOGIN_SUCCESS = """
`+----------------------------+`
`|  ❁ 𝖫𝖮𝖦𝖨𝖭 𝖲𝖴𝖢𝖢𝖤𝖲𝖲𝖥𝖴𝖫𝖫𝖸 ❁  |`
`+----------------------------+`
`|  Your Userbot is now Live  |`
`|  Type .help to get started |`
`+----------------------------+`
"""

ALIVE_TEXT = """
`+----------------------------+`
`|  ❁ 𝖣𝖠𝖱𝖪-𝖴𝖲𝖤𝖱𝖡𝖮𝖳 𝖠𝖫𝖨𝖵𝖤 ❁  |`
`+----------------------------+`
`| Status: Online & Ready     |`
`| Master: MSD 👑             |`
`| Version: 1.0 (DARK)        |`
`+----------------------------+`
"""

# --- DATA PACKS ---
AURA_LINES = [
    "⚡ **Your Aura is too weak to penetrate this domain.**",
    "👑 **The King (MSD) is present. Lower your head.**",
    "🌀 **This chat is protected by an Absolute Void.**",
    "🛑 **Access Denied. You are trying to touch the Sun with bare hands.**",
    "⚜️ **Owner's Aura detected. All unauthorized commands are neutralized.**"
]

SRAID_F = [
    "Dosti gunah hai to hone na dena, Dosti khuda hai to khone na dena. ✨",
    "Log kehte hain zameen par khuda nahi milta, Shayad unhe tum jaisa dost nahi milta. 🤜🤛",
    "Dushman ko bhi hum pakki dua dete hain, Mere dost tujh par to jaan fida karte hain! 🔥"
]

SRAID_L = [
    "Tere chehre mein wo jadoo hai, Ki har koi teri taraf khicha chala aata hai. ✨",
    "Log puchte hain maine aisa kya dekha tujhme, Maine kaha tujhe dekhne ke baad kuch aur nahi dekha. ❤️",
    "Tumhe dekha to ye khayal aaya, Ke jaise sardi mein dhoop ka sath aaya. ☀️"
]

FLIRT = [
    "Are you a Wi-Fi router? Because I’m feeling a very strong connection here. 😉",
    "Kya aapka naam Google hai? Kunki jo bhi main dhoond raha hoon, wo sab aapme hai. 🔍",
    "Do you have a map? I just got lost in your eyes. 🗺️"
]

