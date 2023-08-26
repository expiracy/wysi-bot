import math
from collections import defaultdict

import discord


from score_tracker.score.ScoreDistribution import ScoreDistribution


class Profile:
    def __init__(self, scores):
        self.scores = scores
        self.accuracy = 0.0
        self.raw_pp = 0.0
        self.weighted_pp = 0.0

        self.score_distribution = ScoreDistribution(self.scores.count(), 0, defaultdict(int))
        self.calculate_stats(scores)

    def calculate_stats(self, scores):
        factor = 1

        for score_index, score in enumerate(scores.scores):
            self.score_distribution.mods_counts[int(score.id.mods)] += 1
            self.raw_pp += score.info.pp
            self.weighted_pp += score.info.pp * factor
            self.accuracy += score.info.accuracy * factor

            if score.info.combo == score.beatmap.max_combo:
                self.score_distribution.fcs += 1

            factor *= 0.95

        if scores.count() > 0:
            self.accuracy /= (20 * (1 - math.pow(0.95, scores.count())))

        self.accuracy = round(self.accuracy, 2)
        self.weighted_pp = round(self.weighted_pp, 1)

    def __str__(self):
        return (f"**Accuracy:** {self.accuracy} %\n"
                f"**Weighted PP:** {self.weighted_pp} PP\n"
                f"**Raw PP:** {self.raw_pp} PP")

    def embed(self, user):
        embed = discord.Embed(colour=user.colour)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_author(name=f"{user.name}'s Profile", icon_url=user.avatar.url)
        embed.add_field(name="", value=str(self), inline=False)
        return embed
