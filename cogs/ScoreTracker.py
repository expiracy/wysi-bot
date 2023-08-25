import asyncio
import csv
import re

import discord
from discord.ext import commands
from discord.ext.commands import Context

from WYSIBot import osu_api
from score_tracker.Buttons import ProfileButtons, ScoresButtons, TrackedUsersButtons
from score_tracker.Database import Database
from score_tracker.ScoreBeatmap import ScoreBeatmap
from score_tracker.ScoreMods import ScoreMods
from score_tracker.TrackedUsers import TrackedUsers
from score_tracker.UserProfile import UserProfile
from score_tracker.UserScore import UserScore, ConfirmButtons
from score_tracker.UserScores import UserScores


class ScoreTracker(commands.Cog, name="ScoreTracker"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="search_score",
        description="Search for substring in scores.",
    )
    async def search_scores(self, context: Context, search_term):
        scores = Database().search_scores(context.author.id, search_term)
        scores = UserScores(context.author.id, scores)
        return await context.send(embed=scores.get_embed(context.author, f"{context.author.name}'s Scores (Search Term: `{search_term}`)"))

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
        if context.author.id not in {403305665113751572, 187907815711571977}:
            return await context.send("You cannot become cyreu")

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
                mods = ScoreMods(mods)

                if Database().get_score(context.author.id, int(beatmap_id), mods):
                    continue

                beatmap, beatmap_set = await ScoreBeatmap.get_beatmap_and_beatmap_set(beatmap_id)
                score = UserScore(context.author.id, mods, pp, accuracy, row['combo'].split('/')[0], ar,
                                  cs, speed, beatmap, beatmap_set)

                score.add_to_db()

    @commands.hybrid_command(
        name="get_scores",
        description="Gets 5 scores from the provided score_number",
    )
    async def get_scores(self, context: Context, score_number=1):
        scores = UserScores(context.author.id)

        return await context.send(
            embed=scores.get_embed(context.author, f"{context.author.name}'s Scores", score_number),
            view=ScoresButtons(context.author, score_number)
        )

    @commands.hybrid_command(
        name="remove_score",
        description="Removes a score"
    )
    async def remove_score(self, context: Context, beatmap_id: int, mods=None):
        mods = ScoreMods(mods)

        db = Database()
        score = db.get_score(context.author.id, beatmap_id, mods)

        if not score:
            return await context.send(f"No score found for beatmap ID `{beatmap_id}` and mods `{str(mods)}`.")

        db.remove_score(context.author.id, beatmap_id, mods)

        return await context.send(f"Score with beatmap ID `{beatmap_id}` and mods `{str(mods)}` was removed successfully!")

    @commands.hybrid_command(
        name="track",
        description="Tracks a profile's PP"
    )
    async def track(self, context: Context, osu_id):
        try:
            user = await osu_api.user(osu_id, mode="osu")
        except ValueError:
            return await context.send(f"Invalid osu ID provided: `{osu_id}`.")

        Database().add_tracked(context.author.id, osu_id)


        return await context.send(f"Tracking user: `{user.username}`! (to untrack, use `/untrack`)")

    @commands.hybrid_command(
        name="tracked",
        description="Gets tracked users",
    )
    async def tracked(self, context):
        tracked_users = await TrackedUsers.create(context.author)
        return await context.send(
            embed=tracked_users.get_embed(context.author),
            view=TrackedUsersButtons(context.author, tracked_users)
        )

    @commands.hybrid_command(
        name="untrack",
        description="Untrack osu! ID",
    )
    async def untrack(self, context: Context, osu_id):
        Database().remove_tracked(context.author.id, osu_id)
        return await context.send(f"Untracked user with osu! ID: `{osu_id}`!")

    @commands.hybrid_command(
        name="profile",
        description="Get profile stats"
    )
    async def profile(self, context: Context):
        scores = UserScores(context.author.id)

        profile = UserProfile(scores=scores)
        embed = profile.get_embed(context.author)

        return await context.send(embed=embed, view=ProfileButtons(context.author))

    @commands.hybrid_command(
        name="register",
        description="Register your account to be tracked",
    )
    async def register(self, context: Context, osu_id):
        user = await osu_api.user(osu_id, mode="osu")

        if not user:
            return await context.send("Invalid osu user id provided.")

        Database().add_user(context.author.id, osu_id, user.username)

        embed = discord.Embed(title="")
        embed.set_author(name=f"User registered!", icon_url=context.author.avatar.url)

        info = (f"You have linked this discord account to osu username: **{user.username}**\n"
                f"To change the osu username linked to your discord account, run this command again.")

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
            return

        score_embed = rs_message.embeds[0]
        score_info = score_embed.description[1:].split('▸')

        if score_info[0][12] == 'F':
            return

        pp = float(re.findall("\d+.\d+PP", score_info[1])[0][:-2])
        accuracy = float(re.findall("\d+.\d+%", score_info[2])[0][:-1])
        combo = int(re.findall("x\d+/", score_info[4])[0][1:-1])

        beatmap_id = score_embed.author.url.split('/')[-1]
        if "No Mod" in score_embed.author.name:
            mods = ""
        else:
            mods = re.findall("] \+[a-zA-Z]+ \[", score_embed.author.name)[0][3:-2]

        mods = ScoreMods(mods)

        beatmap, beatmap_set = await ScoreBeatmap.get_beatmap_and_beatmap_set(beatmap_id)
        score = UserScore(context.author.id, mods, pp, accuracy, combo, None, None, None, beatmap, beatmap_set)

        expected_player = rs_message.content[32:-3]
        discord_id = Database().get_discord_id(expected_player)

        if not discord_id:
            return

        return await context.send(
            embed=score.get_embed(context.author, f"Add score to {context.author.name}?"),
            view=ConfirmButtons(context.author, score, expected_player)
        )

    @commands.hybrid_command(
        name="add_score",
        description="Adds a score",
    )
    async def add_score(self, context: Context, beatmap_id: int, pp: float, accuracy: float, combo: int,
                        mods=None, ar=None, cs=None, speed=None):

        mods = ScoreMods(mods)

        if int(mods) == -1:
            return await context.send("Invalid mod combo.")

        if not 0 <= accuracy <= 100:
            return await context.send("Invalid accuracy provided.")

        beatmap = await osu_api.beatmap(beatmap_id)

        if not beatmap:
            return await context.send("Invalid beatmap ID provided.")

        if not 0 <= combo <= beatmap.max_combo:
            return await context.send("Provided combo is greater than max combo.")

        beatmap, beatmap_set = await ScoreBeatmap.get_beatmap_and_beatmap_set(beatmap_id)
        score = UserScore(context.author.id, mods, pp, accuracy, combo, ar, cs, speed, beatmap, beatmap_set)
        score.add_to_db()

        return await context.send(
            embed=score.get_embed(context.author, f"Score added to {context.author.name}")
        )


async def setup(bot):
    await bot.add_cog(ScoreTracker(bot))

