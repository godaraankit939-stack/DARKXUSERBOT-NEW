import os
import threading
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    # Render is page ko dekh kar bot ko online rakhega
    return "DARK USERBOT IS LIVE 🚀"

def run_flask():
    # Render hamesha ek 'PORT' variable deta hai, default 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def start_manager():
    # Manager Bot (@BotFather wala) ko start karega
    print("LOG: Starting Manager Bot...")
    subprocess.run(["python3", "main.py"])

def start_userbot():
    # Userbot Engine ko start karega
    print("LOG: Starting Userbot Engine...")
    subprocess.run(["python3", "userbot.py"])

if __name__ == "__main__":
    # 1. Flask ko background thread mein chalana (Port check ke liye)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. Manager Bot ko background thread mein chalana
    manager_thread = threading.Thread(target=start_manager)
    manager_thread.daemon = True
    manager_thread.start()

    # 3. Userbot ko MAIN thread mein chalana
    # Isse script end nahi hogi aur bot chalta rahega
    print("LOG: DARK-USERBOT services are booting up...")
    start_userbot()
    
