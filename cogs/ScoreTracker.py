import asyncio
import csv
import json
import math
import random
import re
import threading
import time
from urllib import request
from discord import InteractionResponse, User

import discord
import requests
from discord.ext import commands
from discord.ext.commands import Context
from ossapi import OssapiAsync

from WYSIBot import config
from score_tracker.Database import Database
from score_tracker.ScoreBeatmap import ScoreBeatmap
from score_tracker.ScoreBeatmapSet import ScoreBeatmapSet
from score_tracker.ScoreMods import ScoreMods
from score_tracker.UserProfile import UserProfile

from score_tracker.UserScore import UserScore
from score_tracker.UserScores import UserScores

osu_api = OssapiAsync(config["client_id"], config["client_secret"])


class NavigationButtons(discord.ui.View):
    def __init__(self, author: User, score_number):
        super().__init__()
        self.author = author
        self.score_number = score_number

    @discord.ui.button(
        label="<<",
        style=discord.ButtonStyle.blurple,
    )
    async def skip_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        self.score_number = 1

        await interaction.response.edit_message(
            embed=UserScores(self.author.id).get_embed(f"{self.author.name}'s Scores", self.author.avatar.url, self.score_number),
            view=NavigationButtons(self.author, self.score_number)
        )

    @discord.ui.button(
        label="<",
        style=discord.ButtonStyle.blurple,
    )
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        scores = UserScores(self.author.id)
        self.score_number -= 5

        if self.score_number == -4:
            self.score_number = max(1, len(scores.scores) - 4)
        elif 0 >= self.score_number > -4:
            self.score_number = 1

        await interaction.response.edit_message(
            embed=scores.get_embed(f"{self.author.name}'s Scores", self.author.avatar.url, self.score_number),
            view=NavigationButtons(self.author, self.score_number)
        )

    @discord.ui.button(
        label=">",
        style=discord.ButtonStyle.blurple,
    )
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        scores = UserScores(self.author.id)
        self.score_number += 5

        if self.score_number > len(scores.scores):
            self.score_number = 1

        await interaction.response.edit_message(
            embed=scores.get_embed(f"{self.author.name}'s Scores", self.author.avatar.url, self.score_number),
            view=NavigationButtons(self.author, self.score_number)
        )

    @discord.ui.button(
        label=">>",
        style=discord.ButtonStyle.blurple,
    )
    async def skip_end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        scores = UserScores(self.author.id)
        self.score_number = max(1, len(scores.scores) - 4)

        await interaction.response.edit_message(
            embed=scores.get_embed(f"{self.author.name}'s Scores", self.author.avatar.url, self.score_number),
            view=NavigationButtons(self.author, self.score_number)
        )


class ConfirmButtons(discord.ui.View):
    def __init__(self, author: User, score, expected_player):
        super().__init__()
        self.author = author
        self.score = score
        self.expected_player = expected_player

    @discord.ui.button(
        label="Add",
        style=discord.ButtonStyle.green,
    )
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = Database().get_osu_username(interaction.user.id)

        if interaction.user.id != self.author.id or not player or self.expected_player != player[0]:
            return

        last_embed = interaction.message.embeds[0]

        self.score.add_to_db()
        last_embed.set_author(name="Score added!", icon_url=last_embed.author.icon_url)
        await interaction.response.edit_message(embed=last_embed, view=None)

    @discord.ui.button(
        label="Ignore",
        style=discord.ButtonStyle.red,
    )
    async def ignore(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = Database().get_osu_username(interaction.user.id)

        if interaction.user.id != self.author.id or not player or self.expected_player != player[0]:
            return

        await interaction.response.edit_message(delete_after=True)


class ScoreTracker(commands.Cog, name="ScoreTracker"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="always_fc",
        description="stop being cyreu",
    )
    async def always_fc(self, context: Context):
        Database().remove_scores(context.author.id)
        return await context.send(f"{context.author.mention} is no longer cyreu!")

    @commands.hybrid_command(
        name="become_cyreu",
        description="never fc"
    )
    async def never_fc(self, context: Context):
        with open("cyreu.csv", 'r') as file:

            reader = csv.DictReader(file)

            await context.send(f"{context.author.mention} has become cyreu!")

            for row in reader:
                split_mods = row['mods'].split(',')
                mods = split_mods[0]

                if mods[-1] == 'x':
                    if mods[-5].isalpha():
                        speed = float(mods[-4:-1])
                        mods = mods[:-4]
                    else:
                        speed = float(mods[-5:-1])
                        mods = mods[:-5]

                else:
                    speed = None

                beatmap_id = row['id']

                if not beatmap_id:
                    break

                ar = re.findall("ar\d+.\d+", split_mods[1])
                cs = re.findall("cs\d+.\d+", split_mods[1])

                if ar:
                    ar = float(ar[0][2:])
                else:
                    ar = None

                if cs:
                    cs = float(cs[0][2:])
                else:
                    cs = None

                accuracy = row['acc']
                pp = row['raw pp']

                beatmap, beatmap_set = await UserScore.get_beatmap_and_beatmap_set(beatmap_id)
                score = UserScore(context.author.id, ScoreMods(mods=mods), pp, accuracy, row['combo'].split('/')[0], ar,
                                  cs, speed, beatmap, beatmap_set)
                score.add_to_db()

    @commands.hybrid_command(
        name="get_scores",
        description="Gets 5 scores from the provided score_number",
    )
    async def get_scores(self, context: Context, score_number=1):
        scores = UserScores(context.author.id)

        return await context.send(
            embed=scores.get_embed(f"{context.author}'s Scores", context.author.avatar.url, score_number),
            view=NavigationButtons(context.author, score_number)
        )

    @commands.hybrid_command(
        name="profile",
        description="Get profile stats"
    )
    async def profile(self, context: Context):
        scores = Database().get_scores(context.author.id)
        profile = UserProfile(scores)

        embed = discord.Embed()
        embed.set_author(name=f"{context.author.name}'s Profile", icon_url=context.author.avatar.url)

        info = f'''**Scores:** {len(scores)}
        **PP (Weighted):** {profile.weighted_pp} PP
        **PP (Raw):** {profile.raw_pp} PP
        **Accuracy: ** {profile.accuracy} %
        **FCs: **{profile.fcs}'''

        embed.add_field(name="", value=info)

        # TODO allow user to change this
        expiracy = (await osu_api.user(14415546))
        karan = (await osu_api.user(19813440))
        kyarin = (await osu_api.user(15752228))
        incognito_mercy = (await osu_api.user(12838922))

        profile_snipes = f"**PP Differences**\n"
        profile_snipes += f"[{expiracy.username}](https://osu.ppy.sh/users/{expiracy.id}): ∞\n"
        profile_snipes += f"[{karan.username}](https://osu.ppy.sh/users/{karan.id}): {round(karan.statistics.pp - profile.weighted_pp, 1)}\n"
        profile_snipes += f"[{kyarin.username}](https://osu.ppy.sh/users/{kyarin.id}): {round(kyarin.statistics.pp - profile.weighted_pp, 1)}\n"
        profile_snipes += f"[{incognito_mercy.username}](https://osu.ppy.sh/users/{incognito_mercy.id}): {round(incognito_mercy.statistics.pp - profile.weighted_pp, 1)}"

        embed.add_field(name="", value=profile_snipes, inline=False)

        return await context.send(embed=embed)

    @commands.hybrid_command(
        name="register",
        description="Register your account to be tracked",
    )
    async def register(self, context: Context, osu_username):
        user = await osu_api.user(user=osu_username)

        if not user:
            return await context.send("Invalid osu user id provided.")

        Database().add_user(context.author.id, osu_username)

        embed = discord.Embed(title="")
        embed.set_author(name=f"User registered!", icon_url=context.author.avatar.url)

        info = f'''You have linked this discord account to osu username: {osu_username}
        To change the osu username linked to your discord account, please run this command again.'''

        embed.add_field(name="", value=info)
        return await context.send(embed=embed)

    @commands.command(
        name="rs",
    )
    async def auto_add_score(self, context: Context):
        rs_message = context.channel.last_message

        while rs_message.author.id != 289066747443675143:
            await asyncio.sleep(0.5)
            rs_message = context.channel.last_message

        if not rs_message.embeds:
            return await context.message.add_reaction("🏃‍♂️")

        score_embed = rs_message.embeds[0]
        score_info = score_embed.description[1:].split('▸')

        if score_info[0][12] == 'F':
            return await context.message.add_reaction("🏃‍♂️")

        pp = float(re.findall("\d+.\d+PP", score_info[1])[0][:-2])
        accuracy = float(re.findall("\d+.\d+%", score_info[2])[0][:-1])
        combo = int(re.findall("x\d+/", score_info[4])[0][1:-1])

        beatmap_id = score_embed.author.url.split('/')[-1]

        mods = re.findall("] \+[A-Z]+ \[", score_embed.author.name)[0][3:-2]

        beatmap, beatmap_set = await UserScore.get_beatmap_and_beatmap_set(beatmap_id)
        score = UserScore(context.author.id, ScoreMods(mods=mods), pp, accuracy, combo, None, None, None, beatmap,
                          beatmap_set)

        expected_player = rs_message.content[32:-3]
        discord_id = Database().get_discord_id(expected_player)

        if not discord_id:
            return await context.message.add_reaction("🏃‍♂️")

        return await context.send(
            embed=score.get_embed(context.author, f"Add score to {context.author.name}?"),
            view=ConfirmButtons(context.author, score, expected_player)
        )

    @commands.hybrid_command(
        name="add_score",
        description="Adds a score",
    )
    async def add_score(self, context: Context, beatmap_id=3920486, pp=0.0, accuracy=100.0, combo=1,
                        mods="", ar=None, cs=None, speed=None):

        mods = ScoreMods(mods=mods)

        if int(mods) == -1:
            return await context.send("Invalid mod combo.")

        if not 0 <= accuracy <= 100:
            return await context.send("Invalid accuracy provided.")

        beatmap = await osu_api.beatmap(beatmap_id)

        if not beatmap:
            return await context.send("Invalid beatmap ID provided.")

        if not 0 <= combo <= beatmap.max_combo:
            return await context.send("Provided combo is greater than max combo.")

        beatmap, beatmap_set = await UserScore.get_beatmap_and_beatmap_set(beatmap_id)
        score = UserScore(context.author.id, mods, pp, accuracy, combo, ar, cs, speed, beatmap, beatmap_set)
        score.add_to_db()

        return await context.send(embed=score.get_embed(context.author, f"Score added for {context.author.name}"))


async def setup(bot):
    await bot.add_cog(ScoreTracker(bot))
