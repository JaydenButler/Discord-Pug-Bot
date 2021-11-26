from datetime import datetime, timedelta
import logging
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from Managers.QueueManager import queueManagers

global BOTCONFIG

load_dotenv(".env")

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guild_messages = True

initial_extensions = ["cogs.commands", "cogs.admin_commands"]

bot = commands.Bot(command_prefix="!", intents=intents)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@tasks.loop(minutes = 1)
async def check_queues():
    for queueManager in queueManagers:
        for player in queueManager.GetCurrentQueue().players:
            elapsed = datetime.now() - player.timeQueued
            if elapsed > timedelta(minutes=player.queueLengthTime):
                queueManager.GetCurrentQueue().players.remove(player)
                user = await bot.fetch_user(player.id)
                await user.send("You were removed from the queue due to inactivity. Please re queue if you wish to play.")

@bot.event
async def on_ready():
    check_queues.start()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot.remove_command("help")
bot.run(os.environ.get("BOT_TOKEN"), reconnect=True)