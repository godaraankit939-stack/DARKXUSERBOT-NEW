import os
import threading
import time
from flask import Flask

# 1. Flask App Setup (Railway/Render ke liye)
app = Flask(__name__)

@app.route('/')
def hello():
    return "DARK USERBOT IS LIVE 🚀", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    print(f"LOG: Port binding on {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# 2. Main Execution
if __name__ == "__main__":
    # Flask ko background thread mein start karna taaki health check pass ho
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # 2 second ka wait taaki Port bind ho jaye
    time.sleep(2)

    # LOGIC: Hum sirf main.py ko chalayenge kyunki main.py ke andar 
    # Manager bot aur saare Userbots (sessions) ko load karne ka logic pehle se hai.
    # userbot.py ko alag se chalana session conflict paida karta hai.
    
    print("LOG: DARK-USERBOT Engine starting via main.py...")
    if os.path.exists("main.py"):
        # Ye main process mein chalega jo bot ko band nahi hone dega
        os.system("python3 main.py")
    else:
        print("ERROR: main.py not found in root folder!")
        
