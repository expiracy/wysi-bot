import discord
from discord import User
from ossapi import OssapiAsync
from score_tracker.Database import Database
from score_tracker.ScoreMods import ScoreMods
from score_tracker.ScoreBeatmap import ScoreBeatmap
from score_tracker.ScoreBeatmapSet import ScoreBeatmapSet
from WYSIBot import config


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

        if self.mods:
            score_string += f" + **{str(self.mods)}**"

        if self.speed:
            score_string += f" **({self.speed}x)**"

        score_string += f'''
        **Artist:** {self.beatmap_set.artist}
        **Mapper:** {self.beatmap_set.mapper}
        **PP:** {self.pp} PP | **Accuracy:** {self.accuracy}% | **Combo:** {self.combo}/{self.beatmap.max_combo}x'''

        return score_string

    def get_embed(self, user, title):
        embed = discord.Embed()

        embed.set_author(name=title, icon_url=user.avatar.url)
        embed.set_thumbnail(url=self.beatmap_set.image)
        embed.add_field(name="", value=str(self), inline=False)

        return embed

    def add_to_db(self):
        db = Database()
        db.add_score(self, self.discord_id)
        db.add_beatmap(self.beatmap, self.beatmap_set.beatmap_set_id)
        db.add_beatmap_set(self.beatmap_set)

    @staticmethod
    async def get_beatmap_and_beatmap_set(beatmap_id):
        osu_api = OssapiAsync(config["client_id"], config["client_secret"])

        beatmap = await osu_api.beatmap(beatmap_id)
        beatmap_set = beatmap._beatmapset

        user = await osu_api.user(beatmap.user_id)

        if user:
            mapper = user.username
        else:
            mapper = ""

        beatmap = ScoreBeatmap(beatmap_id, beatmap.version, beatmap.difficulty_rating, beatmap.max_combo)
        beatmap_set = ScoreBeatmapSet(beatmap_set.id, beatmap_set.title, beatmap_set.artist, beatmap_set.covers.list, mapper)

        return beatmap, beatmap_set


