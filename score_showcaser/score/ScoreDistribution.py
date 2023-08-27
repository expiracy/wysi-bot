import discord

from score_showcaser.score.Mods import Mods


class ScoreDistribution:
    def __init__(self, count, fcs, mods_counts):
        self.count = count
        self.fcs = fcs
        self.mods_counts = mods_counts

    def __str__(self):
        scores_string = (f"**Total:** {self.count}\n"
                         f"**FCs:** {self.fcs} ({round(100 * self.fcs / self.count, 2)} %)\n")

        sorted_frequencies = sorted(self.mods_counts.items(), key=lambda x: x[1], reverse=True)

        for encoded_mods, count in sorted_frequencies:
            mods = Mods(encoded_mods)

            if str(mods):
                scores_string += f"**{str(mods)}:** "
            else:
                scores_string += f"**No Mod:** "

            scores_string += f"{count} ({round(100 * count / self.count, 2)} %)\n"

        scores_string = scores_string[:-1]

        return scores_string

    def embed(self, user):
        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=f"{user.name}'s Score Type Distribution", icon_url=user.avatar.url)
        embed.add_field(name="", value=str(self), inline=False)
        return embed
