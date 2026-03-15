import os
import threading
from dotenv import load_dotenv
from server import create_app
from bot import OrderBot
import discord

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
base_url = os.getenv("BASE_URL", "http://localhost:3000")
port = int(os.getenv("PORT", "3000"))

if not token:
    raise SystemExit("Missing DISCORD_TOKEN in .env")


def run_server():
    app = create_app()
    app.run(host="0.0.0.0", port=port)


server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

intents = discord.Intents.default()
intents.message_content = True

client = OrderBot(base_url=base_url, intents=intents)
client.run(token)
