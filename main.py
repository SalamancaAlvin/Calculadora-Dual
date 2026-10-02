import os
import random
import threading
from flask import Flask
import discord
from discord.ext import commands

# Servidor web en segundo plano para mantener activo el servicio en Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Discord activo", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado exitosamente como: {bot.user}")

# --- COMANDOS GENERALES Y UTILIDADES ---

@bot.command()
async def ping(ctx):
    """Muestra la latencia actual del bot."""
    latencia = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latencia: {latencia}ms")

@bot.command()
async def hola(ctx):
    """Saluda al usuario."""
    await ctx.send(f"Hola {ctx.author.mention}, ¿en qué te puedo ayudar?")

@bot.command()
async def decir(ctx, *, mensaje: str):
    """Repite el texto escrito después del comando."""
    await ctx.send(mensaje)

@bot.command()
async def avatar(ctx, usuario: discord.Member = None):
    """Muestra el avatar del usuario con formato Embed elegante."""
    usuario = usuario or ctx.author

    # Obtener URLs en diferentes formatos
    png_url = usuario.display_avatar.with_format("png").url
    jpg_url = usuario.display_avatar.with_format("jpg").url
    webp_url = usuario.display_avatar.with_format("webp").url

    # Crear el Embed personalizado
    embed = discord.Embed(
        title=f"Avatar de {usuario.display_name}",
        description=f"[PNG]({png_url}) | [JPG]({jpg_url}) | [WEBP]({webp_url})",
        color=0xD35400
    )

    # Detectar decoración de avatar
    decoracion_nombre = "Ninguna"
    if getattr(usuario, "avatar_decoration", None):
        decoracion_nombre = usuario.avatar_decoration.name or "Equipada"

    embed.add_field(name="Decoración de avatar", value=decoracion_nombre, inline=False)
    embed.set_image(url=usuario.display_avatar.url)
    embed.set_footer(text="Detrás de cada avatar, hay un mundo por descubrir.")

    # Botón tipo enlace
    view = discord.ui.View()
    boton = discord.ui.Button(
        label="Ver en navegador",
        url=usuario.display_avatar.url,
        style=discord.ButtonStyle.link
    )
    view.add_item(boton)

    await ctx.send(embed=embed, view=view)

@bot.command()
async def userinfo(ctx, usuario: discord.Member = None):
    """Muestra detalles sobre una cuenta."""
    usuario = usuario or ctx.author
    creacion = usuario.created_at.strftime("%d/%m/%Y")
    ingreso = usuario.joined_at.strftime("%d/%m/%Y") if usuario.joined_at else "Desconocida"
    
    info = (
        f"Información de {usuario.name}:\n"
        f"- ID: {usuario.id}\n"
        f"- Cuenta creada: {creacion}\n"
        f"- Ingreso al servidor: {ingreso}\n"
        f"- Rol principal: {usuario.top_role.name}"
    )
    await ctx.send(info)

@bot.command()
async def serverinfo(ctx):
    """Muestra datos principales del servidor."""
    servidor = ctx.guild
    info = (
        f"Servidor: {servidor.name}\n"
        f"- ID: {servidor.id}\n"
        f"- Creador: {servidor.owner}\n"
        f"- Miembros totales: {servidor.member_count}\n"
        f"- Canales totales: {len(servidor.channels)}"
    )
    await ctx.send(info)

# --- DIVERSIÓN Y JUEGOS ---

@bot.command(name="8ball")
async def ocho_ball(ctx, *, pregunta: str):
    """Responde preguntas con la bola 8 mágica."""
    respuestas = [
        "En mi opinión, sí.",
        "Es decididamente así.",
        "Sin duda alguna.",
        "Sí, definitivamente.",
        "Puedes confiar en ello.",
        "Respuesta vaga, vuelve a intentarlo.",
        "Pregunta en otro momento.",
        "Mejor no decirte ahora.",
        "No cuentes con ello.",
        "Mi respuesta es no.",
        "Mis fuentes dicen que no.",
        "Muy dudoso."
    ]
    await ctx.send(f"Pregunta: {pregunta}\nRespuesta: {random.choice(respuestas)}")

@bot.command()
async def dado(ctx, caras: int = 6):
    """Lanza un dado del número de caras especificado (6 por defecto)."""
    resultado = random.randint(1, caras)
    await ctx.send(f"Lanzaste un dado de {caras} caras y salió: {resultado}")

@bot.command()
async def moneda(ctx):
    """Lanza una moneda al aire."""
    resultado = random.choice(["Cara", "Cruz"])
    await ctx.send(f"Resultado: {resultado}")

@bot.command()
async def elegir(ctx, *opciones):
    """Elige una opción al azar separada por espacios."""
    if len(opciones) < 2:
        await ctx.send("Debes darme al menos 2 opciones separadas por espacios.")
        return
    seleccion = random.choice(opciones)
    await ctx.send(f"Opción elegida: {seleccion}")

@bot.command()
async def chiste(ctx):
    """Cuenta un chiste corto aleatorio."""
    chistes = [
        "¿Qué le dice un bit a otro? Nos vemos en el bus.",
        "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
        "¿Qué hace una abeja en el gimnasio? Zum-ba.",
        "Hay 10 tipos de personas en el mundo: las que entienden binario y las que no.",
        "¿Qué le dice una impresora a otra? ¿Esa hoja es tuya o es impresión mía?"
    ]
    await ctx.send(random.choice(chistes))

@bot.command()
async def ruleta(ctx):
    """Juego de ruleta rusa con probabilidad de 1 entre 6."""
    bala = random.randint(1, 6)
    if bala == 1:
        await ctx.send(f"PUM! {ctx.author.mention} no sobrevivió a la ruleta.")
    else:
        await ctx.send(f"Clic! {ctx.author.mention} se salvó. Siguiente turno.")

# --- MODERACIÓN ---

@bot.command()
@commands.has_permissions(manage_messages=True)
async def limpiar(ctx, cantidad: int = 5):
    """Borra la cantidad especificada de mensajes."""
    await ctx.channel.purge(limit=cantidad + 1)
    await ctx.send(f"Se eliminaron {cantidad} mensajes.", delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, usuario: discord.Member, *, razon: str = "Sin razón especificada"):
    """Expulsa a un miembro del servidor."""
    await usuario.kick(reason=razon)
    await ctx.send(f"Usuario {usuario.name} expulsado. Razón: {razon}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, usuario: discord.Member, *, razon: str = "Sin razón especificada"):
    """Banea a un miembro del servidor."""
    await usuario.ban(reason=razon)
    await ctx.send(f"Usuario {usuario.name} baneado. Razón: {razon}")

# Manejo de errores
@kick.error
@ban.error
@limpiar.error
async def errores_moderacion(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No tienes los permisos requeridos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Falta especificar un argumento obligatorio (usuario o cantidad).")

# Iniciar bot
token = os.getenv("DISCORD_TOKEN")

if token:
    bot.run(token)
else:
    print("Error: No se encontró la variable de entorno DISCORD_TOKEN en Render.")
