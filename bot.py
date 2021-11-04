import logging
import discord
from discord.ext import commands
from dotenv import dotenv_values

config = dotenv_values(".env")

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guild_messages = True

initial_extensions = ["cogs.commands"]

bot = commands.Bot(command_prefix="!", intents=intents)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot.run(config["BOT_TOKEN"], reconnect=True)