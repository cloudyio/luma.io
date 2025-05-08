import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='ping', description='Le ping')
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"pong")

async def setup(bot):
    await bot.add_cog(Ping(bot))