import discord
from discord import User


class TrackedUsers:
    USERS_PER_PAGE = 5

    def __init__(self, tracked_users):
        self.tracked_users = list(sorted(tracked_users, key=lambda user: user.pp, reverse=True))

    def count(self):
        return len(self.tracked_users)

    def embed(self, user: User, profile, lower=0):
        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=f"{user.name}'s Tracked Users", icon_url=user.avatar.url)

        for i, tracked_user in enumerate(self.tracked_users[lower:lower + TrackedUsers.USERS_PER_PAGE]):
            if i == 0:
                embed.set_thumbnail(url=tracked_user.image)

            user_pp = tracked_user.pp
            user_acc = tracked_user.accuracy

            tracked_user_string = (f"[**{tracked_user.username}**](https://osu.ppy.sh/u/{tracked_user.id})\n"
                                   f"**PP:** {user_pp} ({round(user_pp - profile.weighted_pp, 2):+} PP)\n"
                                   f"**Accuracy:** {round(user_acc, 2)} % ({round(user_acc - profile.accuracy, 2):+} %)")

            embed.add_field(name="", value=tracked_user_string, inline=False)

        return embed



