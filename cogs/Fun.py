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


class Fun(commands.Cog, name="Fun"):
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


async def setup(bot):
    await bot.add_cog(Fun(bot))
