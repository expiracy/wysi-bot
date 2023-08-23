import discord

from cogs.ScoreTracker import osu_api
from score_tracker.Database import Database
from score_tracker.UserProfile import UserProfile
from score_tracker.UserScores import UserScores


class TrackedUsers:
    def __init__(self, discord_id):
        self.profile = UserProfile(UserScores(discord_id))
        self.tracked_ids = Database().get_tracked(discord_id)

    async def get_embed(self, user):
        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=f"{user.name}'s Tracked Users", icon_url=user.avatar.url)

        for osu_id in self.tracked_ids:
            osu_id = osu_id[0]
            try:
                user = await osu_api.user(osu_id, mode="osu")
            except Exception:
                continue

            user_pp = user.statistics.pp
            user_acc = user.statistics.hit_accuracy

            if user.username == "expiracy":
                user_pp = 72727
                user_acc = 100.00

            tracked_user_string = (f"[**{user.username}**](https://osu.ppy.sh/u/{osu_id})\n"
                                   f"**PP:** {user_pp} (You are {round(self.profile.weighted_pp - user_pp, 2):+} PP)\n"
                                   f"**Accuracy:** {round(user_acc, 2)} % (You are {round(self.profile.accuracy - user_acc, 2):+} %)")

            embed.add_field(name="", value=tracked_user_string, inline=False)

        return embed
