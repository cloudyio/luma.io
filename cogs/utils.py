from discord.ext import commands
from db.models.commands import Command
from utils.permissions import CommandErrorType, send_error

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="configcmd")
    @commands.is_owner()
    async def config_command(
        self,
        ctx,
        name: str,
        description: str,
        category: str,
        enabled: bool = True,
        developer_only: bool = False,
        cooldown_seconds: int = 0,
        per_user_cooldown: bool = False,
        enabled_roles: str = "",
        disabled_roles: str = "",
        ignored_roles: str = "",
        allowed_channels: str = "",
        disabled_channels: str = ""
    ):
        """
        Configure a command in the database.
        Usage: !configcmd name description category [enabled] [developer_only] [cooldown_seconds] [per_user_cooldown] [enabled_roles] [disabled_roles] [ignored_roles] [allowed_channels] [disabled_channels]
        
        Role and channel lists should be comma-separated.
        Example: !configcmd ban "Ban a user" moderation true false 10 true "Admin,Mod" "Muted" "" "commands,bot-commands" "general"
        """
        # Convert comma-separated strings to lists
        enabled_roles_list = [role.strip() for role in enabled_roles.split(",")] if enabled_roles else []
        disabled_roles_list = [role.strip() for role in disabled_roles.split(",")] if disabled_roles else []
        ignored_roles_list = [role.strip() for role in ignored_roles.split(",")] if ignored_roles else []
        allowed_channels_list = [channel.strip() for channel in allowed_channels.split(",")] if allowed_channels else []
        disabled_channels_list = [channel.strip() for channel in disabled_channels.split(",")] if disabled_channels else []

        # Create permissions dictionary
        permissions = {
            "enabled_roles": enabled_roles_list,
            "disabled_roles": disabled_roles_list,
            "ignored_roles": ignored_roles_list,
            "allowed_channels": allowed_channels_list,
            "disabled_channels": disabled_channels_list
        }

        # Create cooldown dictionary
        cooldown = {
            "seconds": cooldown_seconds,
            "per_user": per_user_cooldown
        }

        # Create command object
        command = Command(
            name=name,
            description=description,
            category=category,
            enabled=enabled,
            guild_id=str(ctx.guild.id),
            permissions=permissions,
            cooldown=cooldown,
            developer_only=developer_only
        )

        try:
            # Try to update if exists, insert if not
            existing_command = await Command.find_by_name_and_guild(name, str(ctx.guild.id))
            if existing_command:
                command._id = existing_command._id
                await command.update_one()
                await ctx.send(f"✅ Updated command '{name}' configuration.")
            else:
                await command.insert_one()
                await ctx.send(f"✅ Added new command '{name}' configuration.")
        except Exception as e:
            await send_error(ctx, CommandErrorType.SETUP)
            print(f"Error configuring command: {e}")

    @config_command.error
    async def config_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await send_error(ctx, CommandErrorType.DEVELOPER)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument. Use !help configcmd for usage.")
        else:
            await send_error(ctx, CommandErrorType.SETUP)

async def setup(bot):
    await bot.add_cog(Utils(bot)) 