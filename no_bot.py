import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- CONFIGURATION ---
API_URL = 'https://naas.isalman.dev/no' 
STATUS_TEXT = "Saying 'No' to everyone"
# URL for a temporary profile picture
PFP_URL = "https://i.pinimg.com/736x/6a/6d/11/6a6d1124cf69e5588588bc7e397598f6.jpg"

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True  # Required to read mentions/messages
bot = commands.Bot(command_prefix="!", intents=intents)

async def update_profile():
    """Sets the bot's profile picture and status on startup."""
    async with aiohttp.ClientSession() as session:
        async with session.get(PFP_URL) as resp:
            if resp.status == 200:
                pfp_data = await resp.read()
                try:
                    await bot.user.edit(avatar=pfp_data)
                    print("Profile picture updated successfully.")
                except discord.HTTPException:
                    print("Failed to update profile picture (likely ratelimited).")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    # Set the status line
    await bot.change_presence(activity=discord.Game(name=STATUS_TEXT))
    # Update profile picture, Not doing this for now but could be made dynamic in the future.
    # await update_profile()
    print('------')

@bot.event
async def on_message(message):
    # Don't let the bot respond to itself
    if message.author == bot.user:
        return

    # Check if the bot was mentioned
    if bot.user.mentioned_in(message):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        reason = data.get("reason", "I can't even find a reason to say no.")
                        await message.reply(reason)
                    else:
                        await message.reply("The 'No' service is currently unavailable.")
            except Exception as e:
                print(f"Error connecting to local API: {e}")
                await message.reply("Error connecting to the local API service.")

    await bot.process_commands(message)

bot.run(TOKEN)