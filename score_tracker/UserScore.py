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


class ConfirmButtons(discord.ui.View):
    def __init__(self, author: User, score, expected_player):
        super().__init__()
        self.author = author
        self.score = score
        self.expected_player = expected_player

    @discord.ui.button(
        label="Add",
        style=discord.ButtonStyle.green,
    )
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = Database().get_osu_username(interaction.user.id)

        if interaction.user.id != self.author.id or not player or self.expected_player != player[0]:
            return

        embed = interaction.message.embeds[0]

        if self.score.add_to_db(keep_highest=True):
            embed.set_author(name=f"Score added to {self.author.name}", icon_url=embed.author.icon_url)
        else:
            embed.set_author(name=f"Score not added to {self.author.name}", icon_url=embed.author.icon_url)

            error_message = (f"**Beatmap ID and mod combo** has higher or same PP score\n"
                             f"If you need to overwrite the score, use **/add_score**")

            embed.set_field_at(0, name="", value=error_message)

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(
        label="Ignore",
        style=discord.ButtonStyle.red,
    )
    async def ignore(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = Database().get_osu_username(interaction.user.id)

        if interaction.user.id != self.author.id or not player or self.expected_player != player[0]:
            return

        await interaction.response.edit_message(delete_after=True)
