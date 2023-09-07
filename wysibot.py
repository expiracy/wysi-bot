import json
import os
import sys

import discord
from discord.ext import commands
from ossapi import OssapiAsync

# https://discord.com/api/oauth2/authorize?client_id=1013216514532454450&permissions=49469432790903&scope=applications.commands%20bot

try:
    with open(f"{os.path.dirname(__file__)}\\config.json", 'r') as json_file:
        config = json.load(json_file)

except IOError as e:
    sys.exit(f"Could not load config: {e}")

# Setting the intents

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=config['prefix'] + [">"],
    intents=intents,
)

osu_api = OssapiAsync(config["client_id"], config["client_secret"])


@bot.event
async def on_ready():
    for file in os.listdir(f"{os.path.dirname(__file__)}\\cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded cog: {extension}")

            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(exception)

    if config["sync_commands_globally"]:
        await bot.tree.sync()
        print(f'Synced commands')

    print(f'Logged in as {bot.user}')


if __name__ == '__main__':
    bot.run(config['token'])
