import asyncio

import aiohttp
import discord

from WYSIBot import osu_api
from score_tracker.Database import Database
from score_tracker.UserProfile import UserProfile
from score_tracker.UserScores import UserScores


class TrackedUsers:
    def __init__(self, discord_id):
        self.discord_id = discord_id
        self.profile = UserProfile(UserScores(discord_id))
        self.tracked_users = []

    @classmethod
    async def create(cls, author):
        self = TrackedUsers(author.id)
        await self.get_tracked_users()
        return self

    async def fetch_user(self, osu_id, session):
        try:
            user = await osu_api.user(osu_id, mode="osu")
            return user
        except Exception:
            return None

    async def get_tracked_users(self):
        tracked_ids = Database().get_tracked(self.discord_id)

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_user(osu_id[0], session) for osu_id in tracked_ids]
            results = await asyncio.gather(*tasks)
            self.tracked_users = [user for user in results if user is not None]

        self.tracked_users = sorted(self.tracked_users, key=lambda user: user.statistics.pp, reverse=True)

        return self

    def get_embed(self, user, tracked_user_number=1):
        tracked_user_index = tracked_user_number - 1

        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=f"{user.name}'s Tracked Users", icon_url=user.avatar.url)

        for user in self.tracked_users[tracked_user_index:tracked_user_index + 5]:
            user_pp = user.statistics.pp
            user_acc = user.statistics.hit_accuracy

            tracked_user_string = (f"[**{user.username}**](https://osu.ppy.sh/u/{user.id})\n"
                                   f"**PP:** {user_pp} (You are {round(self.profile.weighted_pp - user_pp, 2):+} PP)\n"
                                   f"**Accuracy:** {round(user_acc, 2)} % (You are {round(self.profile.accuracy - user_acc, 2):+} %)")

            embed.add_field(name="", value=tracked_user_string, inline=False)

        return embed


