import discord
from discord import User

from score_tracker.Database import Database
from score_tracker.TrackedUsers import TrackedUsers
from score_tracker.UserProfile import UserProfile
from score_tracker.UserScores import UserScores


class TrackedUsersButtons(discord.ui.View):
    def __init__(self, author: User, tracked_users, tracked_number=1):
        super().__init__()
        self.author = author
        self.tracked_number = tracked_number
        self.tracked_users = tracked_users

    @discord.ui.button(
        label="My Profile",
        style=discord.ButtonStyle.blurple,
    )
    async def tracked(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        scores = UserScores(self.author.id)
        profile = UserProfile(scores=scores)

        return await interaction.response.edit_message(
            embed=profile.get_embed(self.author),
            view=ProfileButtons(self.author)
        )

    @discord.ui.button(
        label="<",
        style=discord.ButtonStyle.blurple,
    )
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        self.tracked_number = max(self.tracked_number - 5, 1)

        await interaction.response.edit_message(
            embed=self.tracked_users.get_embed(self.author, self.tracked_number),
            view=self
        )

    @discord.ui.button(
        label=">",
        style=discord.ButtonStyle.blurple,
    )
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        self.tracked_number = max(1, min(len(Database().get_tracked(self.author.id)) - 4, self.tracked_number + 5))

        await interaction.response.edit_message(
            embed=self.tracked_users.get_embed(self.author, self.tracked_number),
            view=self
        )


class ProfileButtons(discord.ui.View):
    def __init__(self, author: User):
        super().__init__()
        self.author = author

    @discord.ui.button(
        label="Compare to Tracked Users",
        style=discord.ButtonStyle.blurple,
    )
    async def tracked(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        tracked_users = await TrackedUsers.create(self.author)

        return await interaction.response.edit_message(
            embed=tracked_users.get_embed(self.author),
            view=TrackedUsersButtons(self.author, tracked_users)
        )


class ScoresButtons(discord.ui.View):
    def __init__(self, author: User, score_number, title=None):
        super().__init__()
        self.author = author
        self.score_number = score_number
        self.scores = UserScores(self.author.id)

        if not title:
            self.title = f"{self.author.name}'s Scores"
        else:
            self.title = title

    @discord.ui.button(
        label="<<",
        style=discord.ButtonStyle.blurple,
    )
    async def skip_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        self.score_number = 1

        await interaction.response.edit_message(
            embed=self.scores.get_embed(self.author, self.title, self.score_number),
            view=self
        )

    @discord.ui.button(
        label="<",
        style=discord.ButtonStyle.blurple,
    )
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        self.score_number = max(self.score_number - 5, 1)

        await interaction.response.edit_message(
            embed=self.scores.get_embed(self.author, self.title, self.score_number),
            view=self
        )

    @discord.ui.button(
        label=">",
        style=discord.ButtonStyle.blurple,
    )
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        self.score_number = max(1, min(len(self.scores) - 4, self.score_number + 5))

        await interaction.response.edit_message(
            embed=self.scores.get_embed(self.author, self.title, self.score_number),
            view=self
        )

    @discord.ui.button(
        label=">>",
        style=discord.ButtonStyle.blurple,
    )
    async def skip_end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return

        self.score_number = max(1, len(self.scores) - 4)

        await interaction.response.edit_message(
            embed=self.scores.get_embed(self.author, self.title, self.score_number),
            view=self
        )
