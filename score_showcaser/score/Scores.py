import discord


class Scores:
    SCORES_PER_PAGE = 5

    def __init__(self, scores, title):
        self.scores = scores
        self.title = title

    def get(self):
        return self.scores

    def add(self, new_score):
        for i, score in enumerate(self.scores):
            if new_score.info.pp >= score.info.pp:
                self.scores.insert(i, new_score)
                break

        return self

    def count(self):
        return len(self.scores)

    def embed(self, colour, lower=0):

        embed = discord.Embed(title=self.title, colour=colour)

        upper = lower + Scores.SCORES_PER_PAGE

        for i, score in enumerate(self.scores[lower:upper]):
            if i == 0:
                embed.set_thumbnail(url=score.beatmap_set.image)

            embed.add_field(name="", value=f"**{i + lower + 1})** {str(score)}", inline=False)

        return embed
