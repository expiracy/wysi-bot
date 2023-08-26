import discord
from discord import User


class Scores:
    SCORES_PER_PAGE = 5

    def __init__(self, scores, title):
        self.scores = scores
        self.title = title

    def count(self):
        return len(self.scores)

    def embed(self, user: User, lower=0):

        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=self.title, icon_url=user.avatar.url)

        upper = lower + Scores.SCORES_PER_PAGE

        for i, score in enumerate(self.scores[lower:upper]):
            embed.add_field(name="", value=f"**{i + lower + 1})** {str(score)}", inline=False)

        return embed




