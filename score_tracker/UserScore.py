import discord
from discord import User

from score_tracker.Database import Database


class UserScore:
    def __init__(self, discord_id, mods, pp, accuracy, combo, ar, cs, speed, beatmap, beatmap_set):

        self.discord_id = discord_id
        self.mods = mods
        self.pp = pp
        self.accuracy = accuracy
        self.combo = combo
        self.ar = ar
        self.cs = cs
        self.speed = speed

        self.beatmap = beatmap
        self.beatmap_set = beatmap_set

    def __str__(self):
        link = f"https://osu.ppy.sh/b/{self.beatmap.beatmap_id}"
        score_string = f"[**{self.beatmap_set.title}**]({link}) [{self.beatmap.version}]"

        if str(self.mods):
            score_string += f" + **{str(self.mods)}**"

        if self.speed:
            score_string += f" **({self.speed}x)**"

        score_string += (f"\n**Artist:** {self.beatmap_set.artist}\n"
                         f"**Mapper:** {self.beatmap_set.mapper}\n"
                         f"**PP:** {self.pp} PP | **Accuracy:** {self.accuracy}% | **Combo:** x{self.combo}/{self.beatmap.max_combo}")

        return score_string

    def get_embed(self, user: User, title):
        embed = discord.Embed(colour=user.colour)

        embed.set_author(name=title, icon_url=user.avatar.url)
        embed.set_thumbnail(url=self.beatmap_set.image)
        embed.add_field(name="", value=str(self), inline=False)

        return embed

    def add_to_db(self, keep_highest=False):
        db = Database()
        db.add_score(self, self.discord_id, keep_highest)
        db.add_beatmap(self.beatmap, self.beatmap_set.beatmap_set_id)
        db.add_beatmap_set(self.beatmap_set)
