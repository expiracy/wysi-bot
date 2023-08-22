import asyncio
import csv
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
from ossapi import OssapiAsync
from score_tracker.DatabaseManager import DatabaseManager
from score_tracker.OsuModCoder import OsuModCoder

from score_tracker.UserScore import UserScore

osu_api = OssapiAsync(24153, "iRsaNm3TrAZF5EpHxP3ZDLlx4PfOYLcSbU7BbBXC")
db = DatabaseManager()


class NavigationButtons(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(
        label="<",
        style=discord.ButtonStyle.blurple,
    )
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.channel.send("TEST")
        
    @discord.ui.button(
        label=">",
        style=discord.ButtonStyle.blurple,
    )
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.channel.send("TEST")


class ScoreTracker(commands.Cog, name="ScoreTracker"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="steal_scores",
        description="test"
    )
    async def steal_scores(self, context: Context):
        with open("cyreu.csv", 'r') as file:
            print(file)

            reader = csv.DictReader(file)

            for row in reader:
                split_mods = row['mods'].split(',')
                mods = split_mods[0]

                if mods[-1] == 'x':
                    if mods[-5].isalpha():
                        mods = mods[:-4]
                    else:
                        mods = mods[:-5]

                encoded_mods = OsuModCoder.encode(mods)

                map = row['maps']
                beatmap_id = row['id']

                if not beatmap_id:
                    break

                print(map)

                acc = row['acc']

                pp = row['raw pp']

                split_combo = row['combo'].split('/')

                score = UserScore(beatmap_id, encoded_mods, pp, acc, split_combo[0], None, None)
                db.add_score(score, context.author.id)

                beatmap = await osu_api.beatmap(beatmap_id)

                beatmap_set = beatmap._beatmapset

                if not db.get_beatmap(beatmap_id):
                    db.add_beatmap(beatmap)

                mapper = (await osu_api.user(beatmap.user_id))

                if mapper:
                    mapper = mapper.username

                else:
                    mapper = ""

                if not db.get_beatmap_set(beatmap_set.id):
                    db.add_beatmap_set(beatmap_set, mapper)

    @commands.hybrid_command(
        name="get_scores",
        description="Gets scores",
    )
    async def get_scores(self, context: Context):
        scores = db.get_scores(context.author.id)

        embed = discord.Embed()
        embed.set_author(name=f"{context.author.name}'s Scores", icon_url=context.author.avatar.url)

        for score_index, (beatmap_id, mods, pp, accuracy, combo, ar, cs,
                          version, difficulty, max_combo,
                          beatmap_set_id, title, artist, image, mapper) in enumerate(scores):

            print(pp)

            if score_index == 0:
                embed.set_thumbnail(url=image)

            beatmap_info = f"**{score_index + 1}:** [**{title}**](https://osu.ppy.sh/beatmapsets/{beatmap_set_id}#osu/{beatmap_id}) [{version}]"

            if mods:
                beatmap_info += f" + **{OsuModCoder.decode(mods)}**"

            beatmap_info += f"\n**Artist:** {artist}\n**Mapper**: {mapper}\n"

            score_info = f"**PP:** {pp} PP | **Accuracy:** {accuracy}% | **Combo:** {combo}/{max_combo}x"

            embed.add_field(name="", value=beatmap_info + score_info, inline=False)
            embed.add_field(name="", value="", inline=False)

        return await context.send(embed=embed, view=NavigationButtons())

    @commands.hybrid_command(
        name="profile",
        description="Get profile stats"
    )
    async def profile(self, context: Context):
        scores = db.get_scores(context.author.id)

        embed = discord.Embed()
        embed.set_author(name=f"{context.author.name}'s Scores", icon_url=context.author.avatar.url)
        profile_pp = 0

        for score_index, (beatmap_id, mods, pp, accuracy, combo, ar, cs,
                          version, difficulty, max_combo,
                          beatmap_set_id, title, artist, image, mapper) in enumerate(scores):

            profile_pp += pp * 0.95 ** score_index

        return await context.send(str(profile_pp))

    @commands.hybrid_command(
        name="add_score",
        description="Adds a score",
    )
    async def add_score(self, context: Context, beatmap_id=3920486, pp=727.0, accuracy=100.0, combo=7, mods="", ar=None,
                        cs=None):

        encoded_mod = OsuModCoder.encode(mods)

        if encoded_mod == -1:
            return await context.send("Invalid mod combo.")

        mods = OsuModCoder.decode(encoded_mod)

        if not 0 <= accuracy <= 100:
            return await context.send("Invalid accuracy provided.")

        beatmap = await osu_api.beatmap(beatmap_id)

        if not beatmap:
            return await context.send("Invalid beatmap ID provided.")

        if not 0 <= combo <= beatmap.max_combo:
            return await context.send("Provided combo is greater than max combo.")

        beatmap_set = beatmap._beatmapset
        score = UserScore(beatmap_id, mods, pp, accuracy, combo, ar, cs)

        db.add_score(score, context.author.id)

        if not db.get_beatmap(beatmap_id):
            db.add_beatmap(beatmap)

        mapper = (await osu_api.user(beatmap.user_id)).username

        if not db.get_beatmap_set(beatmap_set.id):
            db.add_beatmap_set(beatmap_set, mapper)

        embed = discord.Embed()
        embed.set_author(name=f"Score added for {context.author.name}", icon_url=context.author.avatar.url)
        embed.set_thumbnail(url=beatmap_set.covers.list)

        beatmap_info = f"[**{beatmap_set.title}**]({beatmap.url}) [{beatmap.version}]"

        if mods:
            beatmap_info += f" **+ {mods}**"

        if ar:
            beatmap_info += f" AR: {ar}"

        if cs:
            beatmap_info += f" CS: {cs}"

        beatmap_info += f"\n**Artist:** {beatmap_set.artist}\n**Mapper**: {mapper}"

        print(await osu_api.beatmap_attributes(beatmap_id, mods="HDDT"))

        embed.add_field(name="", value=beatmap_info, inline=False)

        score_info = f"**Accuracy:** {accuracy}%\n**Combo:** {combo}/{beatmap.max_combo}x\n**PP:** {pp} PP"
        embed.add_field(name="", value=score_info, inline=False)

        return await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ScoreTracker(bot))
