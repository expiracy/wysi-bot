import math
from collections import defaultdict

import discord

from score_showcaser.score.Score import Score
from score_showcaser.score.ScoreDistribution import ScoreDistribution


class Profile:
    def __init__(self, scores, tracked_users, image, username):
        self.scores = scores
        self.accuracy = 0.0
        self.raw_pp = 0.0
        self.weighted_pp = 0.0
        self.image = image
        self.username = username

        self.tracked_users = tracked_users

        self.score_distribution = ScoreDistribution(self.scores.count(), 0, defaultdict(int))
        self.calculate_stats(scores)

    def what_if(self, extra_pp, username, colour):
        old_pp = self.weighted_pp

        new_score = Score.blank()
        new_score.info.pp = extra_pp

        new_profile = Profile(self.scores.add(new_score), self.tracked_users, self.image, username)
        new_pp = new_profile.weighted_pp

        embed = discord.Embed(title=f"If {username} got a {extra_pp} PP score...", colour=colour)
        embed.add_field(name="",
                        value=f"**Old PP:** {old_pp}\n**New PP:** {new_pp} PP\n**Change:** {round(new_pp - old_pp, 2):+} PP",
                        inline=False)

        return embed

    def calculate_stats(self, scores):
        factor = 1

        for score_index, score in enumerate(scores.get()):
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
        self.weighted_pp = round(self.weighted_pp, 2)
        self.raw_pp = round(self.raw_pp, 2)

    def __str__(self):
        return (f"**Accuracy:** {self.accuracy} %\n"
                f"**Weighted PP:** {self.weighted_pp} PP\n"
                f"**Raw PP:** {self.raw_pp} PP")

    def embed(self, colour):
        embed = discord.Embed(title=f"Scores Showcase Profile for {self.username}", colour=colour)
        embed.set_thumbnail(url=self.image)
        embed.add_field(name="", value=str(self), inline=False)
        return embed
