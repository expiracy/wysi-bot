import discord

from score_showcaser.score.Mods import Mods


class ScoreDistribution:
    def __init__(self, count, fcs, mods_counts):
        self.count = count
        self.fcs = fcs
        self.mods_counts = mods_counts

    def __str__(self):
        try:
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

        except ZeroDivisionError:
            return ("**No scores added :(**\n"
                    "Please see https://github.com/expiracy/wysi-bot for a list of commands")

    def embed(self, username, colour):
        embed = discord.Embed(title=f"Score Distribution for {username}", colour=colour)
        embed.set_thumbnail(
            url="https://cdn.w600.comps.canstockphoto.com/statistics-stock-illustrations_csp2073945.jpg")
        embed.add_field(name="", value=str(self), inline=False)
        return embed
