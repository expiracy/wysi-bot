import discord
from discord import User


class Score:
    def __init__(self, id, info, beatmap, beatmap_set):
        self.id = id
        self.info = info
        self.beatmap = beatmap
        self.beatmap_set = beatmap_set

    def __str__(self):
        profile_link = f"https://osu.ppy.sh/b/{self.beatmap.id}"
        score_string = f"[**{self.beatmap_set.title}**]({profile_link}) [{self.beatmap.version}] + **{str(self.id.mods)}**"

        if self.info.speed:
            score_string += f" **({self.info.speed}x)**"

        score_string += (f"\n**Artist:** {self.beatmap_set.artist}\n"
                         f"**Mapper:** {self.beatmap_set.mapper}\n"
                         f"**PP:** {self.info.pp} PP | **Accuracy:** {self.info.accuracy}% | **Combo:** x{self.info.combo}/{self.beatmap.max_combo}")

        return score_string

    def embed(self, user: User, title):
        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=title, icon_url=user.avatar.url)
        embed.set_thumbnail(url=self.beatmap_set.image)
        embed.add_field(name="", value=str(self), inline=False)

        return embed


