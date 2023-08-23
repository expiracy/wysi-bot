import math

import discord
from discord.ext import commands
from discord.ext.commands import Context


class Utility(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="transfer_messages",
        description="Transfer channel contents to",
    )
    async def transfer(self, context: Context, destination_channel_id=1141487752169406665):

        destination_channel = self.bot.get_channel(destination_channel_id)

        if not destination_channel:
            return await context.send("Invalid destination channel ID.")

        with open("done.txt", "r+") as file:

            message_ids = file.readlines()
            seen = set(message_ids)

            if message_ids:
                newest_message_id = max(message_ids)
                newest_message = await context.channel.fetch_message(int(newest_message_id))
                history = context.channel.history(limit=50000, oldest_first=True, after=newest_message.created_at)
                counter = len(message_ids) - 1
            else:
                history = context.channel.history(limit=50000, oldest_first=True)
                counter = 1

            async for message in history:
                try:
                    print(counter)
                    counter += 1

                    if message.id not in seen:
                        file.write(f"{message.id}\n")
                    else:
                        continue

                    embed = discord.Embed()
                    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)

                    if message.attachments:
                        await destination_channel.send(embed=embed)

                        for attachment in message.attachments:
                            await destination_channel.send(attachment.url)

                    elif "gif" in message.content:
                        await destination_channel.send(embed=embed)
                        await destination_channel.send(message.content)

                    else:
                        embed.add_field(name="", value=message.content, inline=True)
                        await destination_channel.send(embed=embed)

                except Exception as e:
                    print(e)

    @commands.hybrid_command(
        name="bonus_pp",
        description="Converts: beatmap amount -> bonus PP or bonus PP -> beatmap amount",
    )
    async def bonus_pp(self, context: Context, beatmap_amount=None, bonus_pp=None):

        if beatmap_amount:
            x = int(beatmap_amount)
            res = 416.6667 * (1 - 0.9994 ** x)
            return await context.send(f"{beatmap_amount} beatmaps = {round(res, 4)} bonus pp")

        if bonus_pp:
            x = float(bonus_pp)
            try:
                res = (-math.log((4166667 - 10000 * x) / 4166667) /
                       (3 * math.log(2) + 4 * math.log(5) - math.log(19) - math.log(263)))
                return await context.send(f"{bonus_pp} bonus pp = {round(res)} beatmaps")
            except ValueError:
                return await context.send("Error: max bonus pp is 416.6667 (non inclusive)")

        return await context.send("No args provided.")


async def setup(bot):
    await bot.add_cog(Utility(bot))
