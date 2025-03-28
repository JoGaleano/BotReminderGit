import discord
from discord.ext import tasks
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import json
import os
from dotenv import load_dotenv
load_dotenv()

from zoneinfo import ZoneInfo

ITALY_TZ = ZoneInfo("Europe/Rome")

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DB_PATH = "recordatorios.json"

# Función para cargar recordatorios desde el archivo
def cargar_recordatorios():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return []

# Función para guardar recordatorios al archivo
def guardar_recordatorios(recordatorios):
    with open(DB_PATH, "w") as f:
        json.dump(recordatorios, f, indent=2, default=str)

# Inicializamos recordatorios desde el archivo
recordatorios = cargar_recordatorios()

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")
    await tree.sync(guild=discord.Object(id=GUILD_ID))

@tree.command(name="recordatorio", description="Agrega un recordatorio 📌", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    fecha="Fecha en formato DD-MM",
    hora="Hora en formato HH:MM",
    mensaje="Mensaje del recordatorio"
)
async def recordatorio_command(interaction: discord.Interaction, fecha: str, hora: str, mensaje: str):
    hoy = datetime.now(ZoneInfo("Europe/Rome"))
    try:
        dia, mes = map(int, fecha.split("-"))
        hora_partes = list(map(int, hora.split(":")))
        dt = datetime(hoy.year, mes, dia, hora_partes[0], hora_partes[1], tzinfo=ZoneInfo("Europe/Rome"))
    except:
        await interaction.response.send_message("❌ Fecha u hora con formato incorrecto. Usa DD-MM y HH:MM", ephemeral=True)
        return

    recordatorios.append({
        "usuario_id": interaction.user.id,
        "mensaje": mensaje,
        "fecha_hora": dt.isoformat()
    })
    guardar_recordatorios(recordatorios)
    await interaction.response.send_message(f"✅ Recordatorio guardado para {dt.strftime('%d-%m %H:%M')}", ephemeral=True)

@tasks.loop(seconds=60)
async def revisar_recordatorios():
    ahora = datetime.now(ZoneInfo("Europe/Rome"))
    canal = None
    guild = discord.utils.get(client.guilds, id=GUILD_ID)
    if guild:
        canal = discord.utils.get(guild.text_channels, name="recordatorios")  # cambia el nombre si usas otro canal
    pendientes = [r for r in recordatorios if datetime.fromisoformat(r["fecha_hora"]) <= ahora]
    for r in pendientes:
        user = await client.fetch_user(r["usuario_id"])
        fecha_dt = datetime.fromisoformat(r["fecha_hora"])
        if canal:
            await canal.send(
                f"⏰ <@{r['usuario_id']}> Recordatorio: {r['mensaje']}\n📅 {fecha_dt.strftime('%d-%m %H:%M')}",
                view=RecordatorioView(r)
            )
        else:
            await user.send(f"⏰ Recordatorio: {r['mensaje']}\n📅 {fecha_dt.strftime('%d-%m %H:%M')}")

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    revisar_recordatorios.start()

class RecordatorioView(discord.ui.View):
    def __init__(self, recordatorio):
        super().__init__(timeout=None)
        self.recordatorio = recordatorio

    @discord.ui.button(label="✅ Hecho", style=discord.ButtonStyle.success)
    async def hecho(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.recordatorio in recordatorios:
            recordatorios.remove(self.recordatorio)
            guardar_recordatorios(recordatorios)
            await interaction.response.send_message("✅ Recordatorio marcado como hecho.", ephemeral=True)
            self.stop()

    @discord.ui.button(label="🔁 Posponer 1 hora", style=discord.ButtonStyle.secondary)
    async def posponer(self, interaction: discord.Interaction, button: discord.ui.Button):
        nueva_fecha = datetime.fromisoformat(self.recordatorio["fecha_hora"]) + timedelta(hours=1)
        self.recordatorio["fecha_hora"] = nueva_fecha.isoformat()
        guardar_recordatorios(recordatorios)
        await interaction.response.send_message(f"🔁 Pospuesto para {nueva_fecha.strftime('%d-%m %H:%M')}", ephemeral=True)
        self.stop()

@tree.command(name="misrecordatorios", description="Muestra tus recordatorios pendientes", guild=discord.Object(id=GUILD_ID))
async def mis_recordatorios(interaction: discord.Interaction):
    usuario_id = interaction.user.id
    personales = [r for r in recordatorios if r["usuario_id"] == usuario_id]
    if not personales:
        await interaction.response.send_message("📭 No tienes recordatorios pendientes.", ephemeral=True)
        return

    mensaje = "📝 Tus recordatorios:\n\n"
    for i, r in enumerate(personales, start=1):
        fecha = datetime.fromisoformat(r["fecha_hora"]).strftime("%d-%m %H:%M")
        mensaje += f"{i}. {r['mensaje']} (📅 {fecha})\n"
    await interaction.response.send_message(mensaje, ephemeral=True)

@tree.command(name="borrarrecordatorio", description="Borra uno de tus recordatorios", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(indice="Número del recordatorio (usa /misrecordatorios para verlos)")
async def borrar_recordatorio(interaction: discord.Interaction, indice: int):
    usuario_id = interaction.user.id
    personales = [r for r in recordatorios if r["usuario_id"] == usuario_id]

    if indice < 1 or indice > len(personales):
        await interaction.response.send_message("❌ Índice inválido. Usa /misrecordatorios para ver tus recordatorios.", ephemeral=True)
        return

    recordatorio = personales[indice - 1]
    recordatorios.remove(recordatorio)
    guardar_recordatorios(recordatorios)
    await interaction.response.send_message(f"🗑️ Recordatorio eliminado: {recordatorio['mensaje']}", ephemeral=True)

client.run(TOKEN)