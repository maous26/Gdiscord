#!/usr/bin/env python3
"""
KEEP ALIVE - GEARTED BOT REPLIT
===============================
Maintient le bot en vie sur Replit 24/7
"""

from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return """
    <h1>🤖 Gearted Bot - Status</h1>
    <p>✅ Bot actif et fonctionnel</p>
    <p>🕐 Dernière vérification: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """</p>
    <p>🔗 <a href="https://discord.gg/gearted">Rejoindre Discord</a></p>
    """

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Démarre le serveur web pour maintenir Replit actif"""
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    keep_alive()
    print("🌐 Serveur web démarré sur port 8080")
    
    # Import et démarrage du bot
    try:
        from main import main
        main()
    except Exception as e:
        print(f"❌ Erreur démarrage bot: {e}")
        import traceback
        traceback.print_exc()
