import discord
from utils import permissions
from discord.ext import commands
from utils import utilities

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='prefix', description='Change the bots prefix')
    @permissions.check_perms(command_name='prefix')
    async def prefix(self, ctx: commands.Context, prefix: str):
        try:
            await utilities.update_prefix(str(ctx.guild.id), prefix)
            await ctx.send(f"prefix updated to: `{prefix}`")
        except Exception as e:
            await ctx.send(f"error updating prefix: {str(e)}")

async def setup(bot):
    await bot.add_cog(Utility(bot))