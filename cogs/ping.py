import discord
from discord.ext import commands
from utils.permissions import check_perms

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(name='ping', description='Le ping')
    @check_perms(command_name='ping')
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"pong")

async def setup(bot):
    await bot.add_cog(Ping(bot))