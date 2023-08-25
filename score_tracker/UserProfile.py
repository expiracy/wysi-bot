import math
from collections import defaultdict

import discord
from discord import User

from score_tracker.ScoreMods import ScoreMods


class UserProfile:
    def __init__(self, scores, accuracy=0, raw_pp=0, weighted_pp=0, fcs=0):
        self.scores = scores.scores
        self.accuracy = accuracy
        self.raw_pp = raw_pp
        self.weighted_pp = weighted_pp
        self.fcs = fcs
        self.mods_counter = defaultdict(int)

        self.calculate_stats(self.scores)

    def __str__(self):
        return (f"**Profile Statistics**\n"
                f"**Accuracy:** {self.accuracy} %\n"
                f"**PP:** {self.weighted_pp} PP")

    def get_embed(self, user: User):
        embed = discord.Embed(colour=user.colour)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_author(name=f"{user.name}'s Profile", icon_url=user.avatar.url)

        embed.add_field(name="", value=str(self), inline=False)

        info = (f"**Score Distribution**\n"
                f"**Total:** {len(self.scores)}\n"
                f"**FCs: **{self.fcs} ({round(100 * self.fcs / len(self.scores), 2)} %)")

        mods_info = ""
        sorted_frequencies = sorted(self.mods_counter.items(), key=lambda x: x[1], reverse=True)

        for encoded_mods, count in sorted_frequencies:
            mods = ScoreMods(encoded_mods)

            if str(mods):
                mods_info += f"**{str(mods)}:** "
            else:
                mods_info += f"**No Mod:** "

            mods_info += f"{count} ({round(100 * count / len(self.scores), 2)} %)\n"

        mods_info = mods_info[:-1]

        embed.add_field(name="", value=f"{info}\n{mods_info}", inline=False)

        return embed

    def calculate_stats(self, scores):
        factor = 1

        for score_index, score in enumerate(scores):
            self.mods_counter[int(score.mods)] += 1
            self.raw_pp += score.pp
            self.weighted_pp += score.pp * factor
            self.accuracy += score.accuracy * factor

            if score.combo == score.beatmap.max_combo:
                self.fcs += 1

            factor *= 0.95

        if len(scores) > 0:
            self.accuracy /= (20 * (1 - math.pow(0.95, len(scores))))

        self.accuracy = round(self.accuracy, 2)
        self.weighted_pp = round(self.weighted_pp, 1)
