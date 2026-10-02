import os
import threading
from flask import Flask
import discord
from discord.ext import commands

# Servidor web en segundo plano para responder a UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Discord activo", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Iniciar el servidor web en un hilo secundario
threading.Thread(target=run_flask, daemon=True).start()

# Configuración del bot de Discord
intents = discord.Intents.default()
intents.message_content = True  # Permite al bot leer el contenido de los mensajes

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado exitosamente como: {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Cargar el token desde las variables de entorno de Render
token = os.getenv("DISCORD_TOKEN")

if token:
    bot.run(token)
else:
    print("Error: No se encontró la variable de entorno DISCORD_TOKEN en Render.")
