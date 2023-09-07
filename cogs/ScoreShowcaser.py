import asyncio
import re
import sys

import discord
from discord.ext import commands
from discord.ext.commands import Context

from score_showcaser.Database import Database
from score_showcaser.buttons.Buttons import ProfileButtons, ScoresButtons, AutoScoreButtons
from score_showcaser.score.Beatmap import Beatmap
from score_showcaser.score.BeatmapSet import BeatmapSet
from score_showcaser.score.Mods import Mods
from score_showcaser.score.Score import Score
from score_showcaser.score.ScoreID import ScoreID
from score_showcaser.score.ScoreInfo import ScoreInfo
from score_showcaser.score.ScoresCsvParser import ScoresCsvParser
from wysibot import osu_api


class ScoreDisplayer(commands.Cog, name="ScoreDisplayer"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="add_scores_csv",
        description="Add scores from csv file with exact column titles (mods,map,accuracy,combo,pp)"
    )
    async def add_scores_csv(self, context: Context, scores_csv: discord.Attachment):
        await context.defer()

        scores = await ScoresCsvParser().parse_from_url(str(scores_csv), context.author)

        if not scores.scores:
            return await context.send("Error parsing CSV. Are the column headings like the following?\n"
                                      "`mods,map,accuracy,combo,pp`")

        return await context.send(
            embed=scores.embed(context.author.colour),
            view=ScoresButtons(context.author, scores)
        )

    @commands.hybrid_command(
        name="scores_showcase",
        description="Displays a user's showcased scores",
    )
    async def scores_showcase(self, context: Context, osu_id_or_username=None, score_number=1):
        await context.defer()

        db: Database = Database()

        discord_id = context.author.id
        discord_user = context.author

        if osu_id_or_username:
            discord_id = await db.get_discord_id(osu_id_or_username)

            if not discord_id:
                return await context.send(
                    f"User `{osu_id_or_username}` needs to `/register` to make their score showcase public")

            discord_user = await self.bot.fetch_user(discord_id)

        scores = db.get_scores(discord_id, f"Scores Showcase for {str(discord_user)}")

        if not scores:
            return await context.send(f"No scores added for `{str(discord_user)}` :(\n"
                                      f"`/add` to manually add a score\n"
                                      f"`/register` to get the option to add future `>rs` scores")

        return await context.send(
            embed=scores.embed(context.author.colour, score_number - 1),
            view=ScoresButtons(context.author, scores)
        )

    @commands.hybrid_command(
        name="search_scores_showcase",
        description="Searches for scores",
    )
    async def search_scores_showcase(self, context: Context, search_term: str, osu_id_or_username=None):
        await context.defer()

        db: Database = Database()

        discord_id = context.author.id
        discord_user = context.author

        if osu_id_or_username:
            discord_id = await db.get_discord_id(osu_id_or_username)

            if not discord_id:
                return await context.send(
                    f"User `{osu_id_or_username}` needs to `/register` to make their score showcase public")

            discord_user = await self.bot.fetch_user(discord_id)

        scores = db.get_scores(discord_id, f"Search Term: `{search_term}` in {str(discord_user)}'s Scores Showcase",
                               search_term.lower())

        if not scores:
            return await context.send(f"No scores found for search term `{search_term}` :(")

        return await context.send(
            embed=scores.embed(context.author.colour),
            view=ScoresButtons(context.author, scores)
        )

    @commands.hybrid_command(
        name="backup",
        description="Retrieve db"
    )
    async def backup(self, context: Context):
        if context.author.id != 187907815711571977:
            return await context.send("No permission.")

        return await context.send(file=discord.File(f"{sys.path[1]}/score_showcaser/score_tracker.db"))

    @commands.hybrid_command(
        name="what_if",
        description="Shows the profile if a certain PP score was obtained"
    )
    async def what_if(self, context: Context, pp: int, osu_id_or_username=None):
        await context.defer()

        db: Database = Database()

        discord_id = context.author.id
        discord_user = context.author

        if osu_id_or_username:
            discord_id = await db.get_discord_id(osu_id_or_username)

            if not discord_id:
                return await context.send(
                    f"User `{osu_id_or_username}` needs to `/register` for their stats to be publicly accessed")

            discord_user = await self.bot.fetch_user(discord_id)

        profile = await db.get_user_profile(discord_id, str(discord_user))

        return await context.send(embed=profile.what_if(pp, str(discord_user), context.author.colour))

    @commands.hybrid_command(
        name="profile_showcase",
        description="Gets profile stats for showcased scores ONLY"
    )
    async def profile(self, context: Context, osu_id_or_username=None):
        await context.defer()

        db: Database = Database()

        discord_id = context.author.id
        discord_user = context.author

        if osu_id_or_username:
            discord_id = await db.get_discord_id(osu_id_or_username)

            if not discord_id:
                return await context.send(
                    f"User `{osu_id_or_username}` needs to `/register` to make their profile public")

            discord_user = await self.bot.fetch_user(discord_id)

        profile = await db.get_user_profile(discord_id, str(discord_user))

        return await context.send(
            embed=profile.embed(context.author.colour),
            view=ProfileButtons(context.author, profile)
        )

    @commands.hybrid_command(
        name="add_score_manual",
        description="Adds a score (scores are uniquely identified by beatmap ID and mods)",
    )
    async def add_score_manual(self, context: Context, beatmap_id: int, pp: float, accuracy: float, combo: int,
                               mods=None, ar=None, cs=None, speed=None):

        await context.defer()

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
            embed=score.embed(context.author, f"Score Added to {context.author.name}'s Scores Showcase"),
        )

    @commands.hybrid_command(
        name="register",
        description="Register your account (this will give you the option to add >rs scores automatically)",
    )
    async def register(self, context: Context, osu_id_or_username):
        await context.defer()

        try:
            user = await osu_api.user(osu_id_or_username, mode="osu")
        except ValueError:
            return await context.send(f"Invalid argument provided: `{osu_id_or_username}` :(")

        Database().add_user(context.author.id, user.id, user.username)

        return await context.send(f"Account linked to osu username: `{user.username}`\n"
                                  f"`>rs` will now provide an option to automatically add a score!\n"
                                  f"Your scores showcase and stats will also be publicly accessible!\n"
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

        return await context.send(
            f"Score with beatmap ID `{beatmap_id}` and mods `{str(mods)}` was removed successfully!")

    @commands.hybrid_command(
        name="track",
        description="Tracks a profile's PP"
    )
    async def track(self, context: Context, osu_id_or_username):
        await context.defer()

        try:
            user = await osu_api.user(osu_id_or_username, mode="osu")
        except ValueError:
            return await context.send(f"Invalid argument provided: `{osu_id_or_username}` :(")

        Database().add_tracked(context.author.id, user.id)

        return await context.send(f"Tracking user: `{user.username}`! (to untrack, use `/untrack`)")

    @commands.hybrid_command(
        name="add_score_auto",
        description="Add a score by ID (found on the score page)",
    )
    async def add_score_auto(self, context: Context, score_id):
        await context.defer()

        db: Database = Database()

        try:
            score = await osu_api.score(mode="osu", score_id=score_id)
        except ValueError:
            return await context.send(f"Invalid score ID provided: `{score_id}` :(")

        score_id = ScoreID(context.author.id, score.beatmap.id, Mods(str(score.mods)))
        score_info = ScoreInfo(round(score.pp, 2), round(score.accuracy * 100, 2), score.max_combo, None, None, None)
        beatmap = await Beatmap.from_id(score.beatmap.id)
        beatmap_set = await BeatmapSet.from_id(score.beatmapset.id)
        score = Score(score_id, score_info, beatmap, beatmap_set)

        db.add_score(score)

        return await context.send(
            embed=score.embed(context.author, f"Score Added to {context.author.name}'s Scores Showcase")
        )

    @commands.hybrid_command(
        name="untrack",
        description="Untrack osu player",
    )
    async def untrack(self, context: Context, osu_id_or_username):
        await context.defer()

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
        return await context.send(f"All scores removed for user `{context.author.name}`")

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
    async def rs_add_score(self, context: Context, arg=None):
        db = Database()

        osu_id = db.get_osu_username(context.author.id)

        if not osu_id:
            return

        possible_names = await db.get_osu_usernames(context.author.id)

        if arg and arg not in possible_names:
            return

        # Gets the RS message embed
        rs_message = context.channel.last_message

        while not rs_message.embeds and (
                rs_message.author.id != 289066747443675143 or rs_message.content[32:-3] not in possible_names):
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
            embed=score.embed(context.author, f"Add Score to {context.author.name}'s Scores Showcase?"),
            view=AutoScoreButtons(context.author, score)
        )


async def setup(bot):
    await bot.add_cog(ScoreDisplayer(bot))
