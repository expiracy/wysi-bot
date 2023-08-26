import asyncio
import csv
import re

from discord.ext import commands
from discord.ext.commands import Context

from WYSIBot import osu_api
from score_tracker.Database import Database
from score_tracker.buttons.Buttons import ProfileButtons, TrackedUsersButtons, ScoresButtons, AutoScoreButtons
from score_tracker.score.Beatmap import Beatmap
from score_tracker.score.BeatmapSet import BeatmapSet
from score_tracker.score.Mods import Mods
from score_tracker.score.Score import Score
from score_tracker.score.ScoreID import ScoreID
from score_tracker.score.ScoreInfo import ScoreInfo


class ScoreTracker(commands.Cog, name="ScoreTracker"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="become_cyreu",
        description="never fc"
    )
    async def never_fc(self, context: Context):
        if context.author.id not in {403305665113751572, 187907815711571977}:
            return await context.send("You cannot become `cyreu`! grrrr 🤬🤬")

        db = Database()

        with open("./resources/cyreu.csv", 'r') as file:
            reader = csv.DictReader(file)
            await context.send(f"{context.author.mention} has become `cyreu`!")

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

                mods = Mods(mods)
                score_id = ScoreID(context.author.id, beatmap_id, mods)

                if db.get_score_info(score_id):
                    continue

                pp = row['raw pp']
                accuracy = row['acc']
                combo = row['combo'].split('/')[0]

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

                score_info = ScoreInfo(pp, accuracy, combo, ar, cs, speed)
                beatmap = await Beatmap.from_id(beatmap_id)
                beatmap_set = await BeatmapSet.from_id(beatmap.set_id)

                score = Score(score_id, score_info, beatmap, beatmap_set)
                db.add_score(score)

    @commands.hybrid_command(
        name="get_scores",
        description="Displays a user's scores",
    )
    async def get_scores(self, context: Context, score_number=1):
        scores = Database().get_scores(context.author.id, f"{context.author.name}'s Scores")

        if not scores:
            return await context.send(f"No scores added for `{context.author.name}` :(\n"
                                      f"`/add` to manually add a score\n"
                                      f"`/register` to get the option to add future `>rs` scores")

        return await context.send(
            embed=scores.embed(context.author, score_number - 1),
            view=ScoresButtons(context.author, scores)
        )

    @commands.hybrid_command(
        name="search_scores",
        description="Searches for scores",
    )
    async def search_scores(self, context: Context, search_term: str):
        scores = Database().get_scores(
            context.author.id,
            f"Scores matching search term {search_term} for {context.author.name}",
            search_term
        )

        if not scores:
            return await context.send(f"No scores found for search term `{search_term}` :(")

        return await context.send(
            embed=scores.embed(context.author),
            view=ScoresButtons(context.author, scores)
        )

    @commands.hybrid_command(
        name="tracked",
        description="Gets tracked users",
    )
    async def tracked(self, context, tracked_user_number=1):
        db = Database()
        profile = db.get_user_profile(context.author.id)
        tracked_users = await db.get_tracked_users(context.author.id)

        return await context.send(
            embed=tracked_users.embed(context.author, profile, tracked_user_number - 1),
            view=TrackedUsersButtons(context.author, profile, tracked_users)
        )

    @commands.hybrid_command(
        name="profile",
        description="Gets profile stats for saved scores"
    )
    async def profile(self, context: Context):
        db = Database()
        profile = db.get_user_profile(context.author.id)
        tracked_users = await db.get_tracked_users(context.author.id)

        return await context.send(
            embed=profile.embed(context.author),
            view=ProfileButtons(context.author, profile, tracked_users)
        )

    @commands.hybrid_command(
        name="add_score",
        description="Adds a score (scores are uniquely identified by beatmap ID and mods)",
    )
    async def add_score(self, context: Context, beatmap_id: int, pp: float, accuracy: float, combo: int,
                        mods=None, ar=None, cs=None, speed=None):

        db = Database()
        mods = Mods(mods)

        if int(mods) == -1:
            return await context.send(f"Invalid mod combo: `{str(mods)}`.")

        score_id = ScoreID(context.author.id, beatmap_id, mods)

        if not 0 <= accuracy <= 100:
            return await context.send("Invalid accuracy provided.")

        beatmap = db.get_beatmap(beatmap_id)
        if not beatmap:
            beatmap = await Beatmap.from_id(beatmap_id)

        if not beatmap:
            return await context.send("Invalid beatmap ID provided.")

        if not 0 <= combo <= beatmap.max_combo:
            return await context.send("Provided combo is greater than max combo.")

        beatmap_set = db.get_beatmap_set(beatmap.set_id)
        if not beatmap_set:
            beatmap_set = await BeatmapSet.from_id(beatmap.set_id)

        score_info = ScoreInfo(pp, accuracy, combo, ar, cs, speed)
        score = Score(score_id, score_info, beatmap, beatmap_set)

        db.add_score(score)

        return await context.send(
            embed=score.embed(context.author, f"Score added or replaced!"),
        )

    @commands.hybrid_command(
        name="register",
        description="Register your account (this will give you the option to add >rs scores automatically)",
    )
    async def register(self, context: Context, osu_id_or_username):
        try:
            user = await osu_api.user(osu_id_or_username, mode="osu")
        except ValueError:
            return await context.send(f"Invalid argument provided: `{osu_id_or_username}` :(")

        Database().add_user(context.author.id, user.id, user.username)

        return await context.send(f"Account linked to osu username: `{user.username}`\n"
                                  f"`>rs` will now provide an option to automatically add a score!\n"
                                  f"To change the osu username linked to your discord account, run this command again.")

    @commands.hybrid_command(
        name="remove_score",
        description="Removes a score (scores are uniquely identified by beatmap ID and mods)"
    )
    async def remove_score(self, context: Context, beatmap_id: int, mods=None):
        db = Database()

        mods = Mods(mods)
        score_id = ScoreID(context.author.id, beatmap_id, mods)

        if not db.get_score_info(score_id):
            return await context.send(f"No score found for beatmap ID `{beatmap_id}` and mods `{str(mods)}` :(")

        db.remove_score(score_id)

        return await context.send(f"Score with beatmap ID `{beatmap_id}` and mods `{str(mods)}` was removed successfully!")

    @commands.hybrid_command(
        name="track",
        description="Tracks a profile's PP"
    )
    async def track(self, context: Context, osu_id_or_username):
        try:
            user = await osu_api.user(osu_id_or_username, mode="osu")
        except ValueError:
            return await context.send(f"Invalid argument provided: `{osu_id_or_username}` :(")

        Database().add_tracked(context.author.id, user.id)

        return await context.send(f"Tracking user: `{user.username}`! (to untrack, use `/untrack`)")

    @commands.hybrid_command(
        name="untrack",
        description="Untrack osu player",
    )
    async def untrack(self, context: Context, osu_id_or_username):
        try:
            user = await osu_api.user(osu_id_or_username, mode="osu")
        except ValueError:
            return await context.send(f"Invalid argument provided: `{osu_id_or_username}` :(")

        Database().remove_tracked(context.author.id, user.id)
        return await context.send(f"Untracked user: `{user.username}`!")

    @commands.hybrid_command(
        name="remove_all_scores",
        description="Removes ALL recorded scores (CANNOT BE UNDONE)",
    )
    async def always_fc(self, context: Context):
        Database().remove_scores(context.author.id)
        return await context.send(f"All scores removed for {context.author.name}")

    @commands.hybrid_command(
        name="unregister",
        description="Will unregister you from the best bot",
    )
    async def unregister(self, context: Context):
        Database().remove_user(context.author.id)
        return await context.send(f"Successfully deregistered user `{context.author.name}`!")

    @commands.command(
        name="rs",
    )
    async def auto_add_score(self, context: Context, arg=None):
        db = Database()

        osu_id = db.get_osu_username(context.author.id)

        if not osu_id:
            return

        possible_names = await db.get_osu_usernames(context.author.id)

        if arg and arg not in possible_names:
            return

        # Gets the RS message embed
        rs_message = context.channel.last_message

        while not rs_message.embeds and (rs_message.author.id != 289066747443675143 or rs_message.content[32:-3] not in possible_names):
            await asyncio.sleep(1)
            rs_message = context.channel.last_message

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

        mods = Mods(mods)

        score_id = ScoreID(context.author.id, beatmap_id, mods)

        score_info = ScoreInfo(pp, accuracy, combo, None, None, None)
        beatmap = await Beatmap.from_id(beatmap_id)
        beatmap_set = await BeatmapSet.from_id(beatmap.set_id)

        score = Score(score_id, score_info, beatmap, beatmap_set)

        return await context.send(
            embed=score.embed(context.author, f"Add score to {context.author.name}?"),
            view=AutoScoreButtons(context.author, score)
        )


async def setup(bot):
    await bot.add_cog(ScoreTracker(bot))
