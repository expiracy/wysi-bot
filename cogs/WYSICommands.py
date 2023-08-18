import asyncio
import json
import math
import random
import threading
import time
from urllib import request

import discord
import requests
from discord.ext import commands
from discord.ext.commands import Context


class WYSICommands(commands.Cog, name="WYSICommands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="wysi",
        description="when you see it",
    )
    async def wysi(self, context: Context):
        return await context.send(f"WYSI")

    @commands.hybrid_command(
        name="karan",
        description="nasa",
    )
    async def karan(self, context: Context):
        return await context.send(f"nasa")

    @commands.hybrid_command(
        name="leah_kate",
        description="<3",
    )
    async def leah_kate(self, context: Context):

        options = [
            "10 🌠 your selfish 🤬 ❗ 9 🎇 your jaded 😴 8 💋 The dumbest 🤪 guy I dated!! 🥱 7 🗣️ talk a big game 'til your naked.. 🍤 😳 Only 6 🗿 seconds 💁‍♀️ and I had to fake it 🫢 5 🤢 your toxic! ☢️ 4 🌹 cant 🚫 trust you 😵‍💫 🙅‍♀️ 3 🥉 you still got mommy 👩‍👧 issues ⁉️ 😂 2 🥈 years of your bullshit 💩 😒 i cant undo 1: 🥇 I hate the fact 😖 that you made me love you 💔 ⛓️ 🥀",
            "So drink up 🍻⬆️ , get wasted 🥴️🤢 We only got one shot ☝🔫 , let's waste it 🗑️️ They'll never remember 🙅🧠 what your name is 🔤 No one gives a fuck 🤷🖕 if you're internet famous 🌐🥳️️ So stay up 🚫🛌 , get tattoos 🖋🦵️️ Make out with a stranger 💋🥰️️ in the bathroom 🚻 It's okay to scream it 😆🔊 , if you have to We're totally fucked 😵💀 Life sucks 🌱👎",
            "https://i.ppy.sh/315b23f38b71792e29ea0b9cab1cc6ae6a1d4486/68747470733a2f2f692e696d6775722e636f6d2f7556496b7a75712e706e67",
            "Twinkle 💫twinkle💫 little bitch👌🏼🐶 Just another narcissist👉😎👈 Hate your guts😡😡🫀you👊🏼 make me sick🤒 I'm so fucking over it🤬🤬🤬 Twinkle💫 twinkle💫 little bitch 👌🏼🐶 I wish 🙏you👊🏼 didn't exist🧑🏽❌️ Tried to turn⤵️ my life💔 to shit💩 I'm so fucking over it🤬🤬🤬",
            ".-- .. -. -.- .-.. . 💫/ - .-- .. -. -.- .-.. . 💫 / .-.. .. - - .-.. . / -... .. - -.-. ....👌🏼🐶/ .--- ..- ... - / .- -. --- - .... . .-. / -. .- .-. -.-. .. ... ... .. ... - 👉😎👈/ .... .- - . / -.-- --- ..- .-. / --. ..- - ...😡😡🫀 -.-- --- ..- 👊🏼/ -- .- -.- . / -- . / ... .. -.-. -.-🤒/ .. .----. -- / ... --- / ..-. ..- -.-. -.- .. -. --. / --- ...- . .-. / .. - 🤬🤬🤬/ .-- .. -. -.- .-.. . 💫/ - .-- .. -. -.- .-.. . 💫 / .-.. .. - - .-.. . / -... .. - -.-. ....👌🏼🐶/ .. / .-- .. ... .... / 🙏 -.-- --- ..- 👊🏼/ -.. .. -.. -. .----. - / . -..- .. ... - 🧑🏽❌️/ .-. .. . -.. / - --- / - ..- .-. -. ⤵️/ -- -.-- / .-.. .. ..-. . 💔/ - --- / ... .... .. - 💩/ .. .----. -- / ... --- / ..-. ..- -.-. -.- .. -. --. / --- ...- . .-. / .. - 🤬🤬🤬"
        ]

        return await context.send(options[random.randint(0, len(options) - 1)])

    @commands.hybrid_command(
        name="roll",
        description="Roll for 727",
    )
    async def roll(self, context: Context, upper_bound=1000):
        if context.author.id == 187907815711571977:
            return await context.send(f"{context.author.mention} rolled 727 with an upper bound of {upper_bound}!")

        return await context.send(
            f"{context.author.mention} rolled {random.randint(0, upper_bound)} with an upper bound of {upper_bound}!")

    @commands.hybrid_command(
        name="send",
        description="Secret",
    )
    async def message(self, context: Context, channel, message):
        await context.guild.get_channel(channel).send(message)

    @commands.hybrid_command(
        name="rank_pp",
        description="Converts: pp -> rank or rank -> pp"
    )
    async def rank_pp(self, context: Context):
        pass

    @commands.hybrid_command(
        name="bonus_pp",
        description="Converts: beatmap amount -> bonus PP or bonus PP -> beatmap amount",
    )
    async def bonus_pp(self, context: Context, num_beatmaps=None, bonus_pp=None):

        if num_beatmaps:
            x = int(num_beatmaps)
            res = 416.6667 * (1 - 0.9994 ** x)
            return await context.send(f"{num_beatmaps} beatmaps = {round(res, 4)} bonus pp")

        if bonus_pp:
            x = float(bonus_pp)
            try:
                res = (-math.log((4166667 - 10000 * x) / 4166667) /
                       (3 * math.log(2) + 4 * math.log(5) - math.log(19) - math.log(263)))
                return await context.send(f"{bonus_pp} bonus pp = {round(res)} beatmaps")
            except ValueError:
                return await context.send("Error: max bonus pp is 416.6667 (non inclusive)")

        return await context.send("No args provided.")

    @commands.hybrid_command(
        name="transfer",
        description="Transfer channel contents",
    )
    async def transfer(self, context: Context, destination_channel_id=1141487752169406665):

        destination_channel = self.bot.get_channel(destination_channel_id)

        with open("done.txt", "r+") as file:

            message_ids = file.readlines()
            seen = set(message_ids)

            if message_ids:
                newest_message_id = max(message_ids)
                newest_message = await context.channel.fetch_message(int(newest_message_id))
                history = context.channel.history(limit=50000, oldest_first=True, after=newest_message.created_at)
                counter = len(message_ids) - 1
            else:
                history = context.channel.history(limit=50000, oldest_first=True)
                counter = 1

            async for message in history:
                try:
                    print(counter)
                    counter += 1

                    if message.id not in seen:
                        file.write(f"{message.id}\n")
                    else:
                        continue

                    embed = discord.Embed()
                    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)

                    if message.attachments:
                        await destination_channel.send(embed=embed)

                        for attachment in message.attachments:
                            await destination_channel.send(attachment.url)

                    elif "gif" in message.content:
                        await destination_channel.send(embed=embed)
                        await destination_channel.send(message.content)

                    else:
                        embed.add_field(name="", value=message.content, inline=True)
                        await destination_channel.send(embed=embed)

                except Exception as e:
                    print(e)


async def setup(bot):
    await bot.add_cog(WYSICommands(bot))
