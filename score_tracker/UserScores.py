import discord

from score_tracker.Database import Database
from score_tracker.ScoreBeatmap import ScoreBeatmap
from score_tracker.ScoreBeatmapSet import ScoreBeatmapSet
from score_tracker.ScoreMods import ScoreMods
from score_tracker.UserScore import UserScore


class UserScores:
    def __init__(self, discord_id):
        self.discord_id = discord_id
        scores = Database().get_scores(discord_id)

        self.scores = [UserScore(discord_id, ScoreMods(mods), pp, accuracy, combo, ar, cs, speed,
                                 ScoreBeatmap(beatmap_id, version, difficulty, max_combo),
                                 ScoreBeatmapSet(beatmap_set_id, title, artist, image, mapper))

                       for (beatmap_id, mods, pp, accuracy, combo, ar, cs, speed,
                            version, difficulty, max_combo,
                            beatmap_set_id, title, artist, image, mapper)

                       in scores]

    def get_embed(self, user, title, score_number=1, scores_per_page=5):
        lower_score_index = score_number - 1
        upper_score_index = min(len(self.scores), lower_score_index + scores_per_page)

        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=title, icon_url=user.avatar.url)

        for offset, score in enumerate(self.scores[lower_score_index:upper_score_index]):
            if offset == 0:
                embed.set_thumbnail(url=score.beatmap_set.image)

            embed.add_field(name="", value=f"**{score_number + offset}:** {str(score)}", inline=False)
            embed.add_field(name="", value="", inline=False)

        return embed
