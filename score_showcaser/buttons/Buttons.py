import discord

from score_showcaser.Database import Database
from score_showcaser.score.Scores import Scores
from score_showcaser.user.TrackedUsers import TrackedUsers
from score_showcaser.user.User import User


class ProfileButtons(discord.ui.View):
    def __init__(self, author, profile):
        super().__init__()
        self.author = author
        self.profile = profile

    @discord.ui.button(
        label="Compare",
        style=discord.ButtonStyle.blurple,
    )
    async def tracked(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        return await interaction.response.edit_message(
            embed=self.profile.tracked_users.embed(self.profile.username, self.author.colour, self.profile, 0),
            view=TrackedUsersButtons(self.author, self.profile)
        )

    @discord.ui.button(
        label="Score Distribution",
        style=discord.ButtonStyle.blurple,
    )
    async def score_distribution(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        return await interaction.response.edit_message(
            embed=self.profile.score_distribution.embed(self.profile.username, self.author.colour),
            view=ScoreDistributionButtons(self.author, self.profile)
        )


class TrackedUsersButtons(discord.ui.View):
    def __init__(self, author, profile):
        super().__init__()
        self.author = author
        self.profile = profile
        self.lower_index = 0

    @discord.ui.button(
        label="Profile",
        style=discord.ButtonStyle.blurple,
    )
    async def profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        return await interaction.response.edit_message(
            embed=self.profile.embed(self.author.colour),
            view=ProfileButtons(self.author, self.profile)
        )

    @discord.ui.button(
        label="<",
        style=discord.ButtonStyle.blurple,
    )
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        self.lower_index = max(self.lower_index - 6, 0)

        return await interaction.response.edit_message(
            embed=self.profile.tracked_users.embed(self.profile.username, self.author.colour, self.profile,
                                                   self.lower_index),
            view=self
        )

    @discord.ui.button(
        label=">",
        style=discord.ButtonStyle.blurple,
    )
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        self.lower_index = max(0, min(self.profile.tracked_users.count() - 5,
                                      self.lower_index + 6))

        return await interaction.response.edit_message(
            embed=self.profile.tracked_users.embed(self.profile.username, self.author.colour, self.profile,
                                                   self.lower_index),
            view=self
        )


class ScoresButtons(discord.ui.View):
    def __init__(self, author: User, scores: Scores):
        super().__init__()
        self.author = author
        self.scores = scores
        self.lower_index = 0

    @discord.ui.button(
        label="<<",
        style=discord.ButtonStyle.blurple,
    )
    async def far_last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        self.lower_index = 0

        await interaction.response.edit_message(
            embed=self.scores.embed(self.author.colour, self.lower_index),
            view=self
        )

    @discord.ui.button(
        label="<",
        style=discord.ButtonStyle.blurple,
    )
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        self.lower_index = max(self.lower_index - 5, 0)

        await interaction.response.edit_message(
            embed=self.scores.embed(self.author.colour, self.lower_index),
            view=self
        )

    @discord.ui.button(
        label=">",
        style=discord.ButtonStyle.blurple,
    )
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        self.lower_index = max(0, min(self.scores.count() - 5, self.lower_index + 5))

        await interaction.response.edit_message(
            embed=self.scores.embed(self.author.colour, self.lower_index),
            view=self
        )

    @discord.ui.button(
        label=">>",
        style=discord.ButtonStyle.blurple,
    )
    async def far_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        self.lower_index = max(0, self.scores.count() - 5)

        await interaction.response.edit_message(
            embed=self.scores.embed(self.author.colour, self.lower_index),
            view=self
        )


class ScoreDistributionButtons(discord.ui.View):
    def __init__(self, author: User, profile):
        super().__init__()
        self.author = author
        self.profile = profile

    @discord.ui.button(
        label="Profile",
        style=discord.ButtonStyle.blurple,
    )
    async def far_last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        await interaction.response.edit_message(
            embed=self.profile.embed(self.author.colour),
            view=ProfileButtons(self.author, self.profile)
        )


class AutoScoreButtons(discord.ui.View):
    def __init__(self, author: User, score):
        super().__init__()
        self.author = author
        self.score = score

    @discord.ui.button(
        label="Add",
        style=discord.ButtonStyle.green,
    )
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return

        embed = interaction.message.embeds[0]

        if Database().add_score(self.score, True):
            embed.set_author(name=f"Score added to {self.author.name}!", icon_url=embed.author.icon_url)
        else:
            embed.set_author(name=f"Score not added to {self.author.name} :(", icon_url=embed.author.icon_url)

            error_message = (f"Score not added to {self.author.name}\n"
                             f"**Beatmap ID and mod combo** has higher or same PP score\n"
                             f"If you need to overwrite the score, use `/add_score`")

            embed.set_field_at(0, name="", value=error_message)

        return await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(
        label="Ignore",
        style=discord.ButtonStyle.red,
    )
    async def ignore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        await interaction.response.edit_message(delete_after=True)
