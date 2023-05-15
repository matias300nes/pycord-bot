import discord
import os
from keep_alive import keep_alive
from discord.ext import commands
from discord.ui import Select, View

from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


initial_extensions = []

for file in os.listdir("./commands"):
    if file.endswith(".py"):
        initial_extensions.append(f"commands.{file[:-3]}")

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

keep_alive()

bot.run(os.environ["TOKEN"])
