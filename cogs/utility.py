import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='prefix', description='Change the bots prefix')
    async def prefix(self, ctx: commands.Context, prefix: str):
        await ctx.send(f"Changed prefix to {prefix}")

async def setup(bot):
    await bot.add_cog(Utility(bot))