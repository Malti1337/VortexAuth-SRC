import discord
from discord import app_commands
from discord.ext import commands
import requests

# Replace with your bot token
TOKEN = ""
# Replace with your server API URL
API_URL = ""

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="generate_key", description="Generate a new license key")
async def generate_key(interaction: discord.Interaction):
    response = requests.get(f"{API_URL}/generate_key")
    if response.status_code == 200:
        key = response.json().get("key")
        await interaction.response.send_message(f"Generated key: `{key}`", ephemeral=True)
    else:
        await interaction.response.send_message("Failed to generate key", ephemeral=True)

@bot.tree.command(name="blacklist", description="Blacklist a license key")
@app_commands.describe(license_key="The license key to blacklist")
async def blacklist(interaction: discord.Interaction, license_key: str):
    data = {"license_key": license_key}
    response = requests.post(f"{API_URL}/blacklist", json=data)
    if response.status_code == 200:
        await interaction.response.send_message(f"License key `{license_key}` blacklisted", ephemeral=True)
    else:
        await interaction.response.send_message("Failed to blacklist key", ephemeral=True)

@bot.tree.command(name="reset_hwid", description="Reset HWID for a license key")
@app_commands.describe(license_key="The license key to reset HWID for")
async def reset_hwid(interaction: discord.Interaction, license_key: str):
    data = {"license_key": license_key}
    response = requests.post(f"{API_URL}/reset_hwid", json=data)
    if response.status_code == 200:
        await interaction.response.send_message(f"HWID reset for `{license_key}`", ephemeral=True)
    else:
        await interaction.response.send_message("Failed to reset HWID", ephemeral=True)

bot.run(TOKEN)
