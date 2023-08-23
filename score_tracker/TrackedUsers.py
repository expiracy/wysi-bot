import discord

from cogs.ScoreTracker import osu_api
from score_tracker.Database import Database
from score_tracker.UserProfile import UserProfile
from score_tracker.UserScores import UserScores


class TrackedUsers:
    def __init__(self, discord_id, tracked_users):
        self.profile = UserProfile(UserScores(discord_id))
        self.tracked_users = tracked_users

    def get_embed(self, user):
        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=f"{user.name}'s Tracked Users", icon_url=user.avatar.url)

        for user in self.tracked_users:
            user_pp = user.statistics.pp
            user_acc = user.statistics.hit_accuracy

            if user.username == "expiracy":
                user_pp = 72727
                user_acc = 100.00

            tracked_user_string = (f"[**{user.username}**](https://osu.ppy.sh/u/{user.id})\n"
                                   f"**PP:** {user_pp} (You are {round(self.profile.weighted_pp - user_pp, 2):+} PP)\n"
                                   f"**Accuracy:** {round(user_acc, 2)} % (You are {round(self.profile.accuracy - user_acc, 2):+} %)")

            embed.add_field(name="", value=tracked_user_string, inline=False)

        return embed
