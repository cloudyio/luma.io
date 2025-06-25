from functools import wraps
from typing import Optional, Callable, Any
from enum import Enum
import discord
from discord.ext import commands
from db.models.commands import Command

class CommandErrorType(Enum):
    PERMISSION = "You don't have permission to use this command."
    SETUP = "This command is not set up in this server."
    DISABLED = "This command/module is currently disabled."
    DEVELOPER = "This command is only available to bot developers."
    ROLE_REQUIRED = "You need one of these roles to use this command: {}"
    ROLE_BLOCKED = "You cannot use this command with these roles: {}"
    CHANNEL_ALLOWED = "This command can only be used in: {}"
    CHANNEL_BLOCKED = "This command cannot be used in: {}"
    COOLDOWN = "This command is on cooldown. Try again in {:.1f} seconds."

async def send_error(ctx: commands.Context, error_type: CommandErrorType, *args, delete_after: float = 5.0):
    message = error_type.value.format(*args) if args else error_type.value
    await ctx.send(message, delete_after=delete_after)

class DefaultPermissions:
    ban = discord.Permissions(ban_members=True)
    kick = discord.Permissions(kick_members=True)
    mute = discord.Permissions(manage_roles=True)
    unmute = discord.Permissions(manage_roles=True)
    clear = discord.Permissions(manage_messages=True)
    purge = discord.Permissions(manage_messages=True)

    @classmethod
    def get_permission(cls, permission: str) -> discord.Permissions:
        if permission not in cls.__dict__:
            raise ValueError(f"Invalid permission: {permission}")
        return cls.__dict__[permission]

def check_perms(command_name: str):
    """
    decorator to check if a user has permission to use a command based on:
    - role permissions (enabled/disabled/ignored roles)
    - channel permissions (allowed/disabled channels)
    - command enabled status
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = args[1] if len(args) > 1 else args[0]

            # handle DM case
            if not ctx.guild:
                await send_error(ctx, CommandErrorType.SETUP)
                return

            if ctx.author.permissions.administrator:
                return await func(*args, **kwargs)

            # Get command from database
            try:
                command = await Command.find_by_name_and_guild(command_name, str(ctx.guild.id))
                if not command:
                    try:
                        permission = DefaultPermissions.get_permission(command_name)
                        if ctx.author.has_permissions(permission):
                            return await func(*args, **kwargs)
                        else:
                            await send_error(ctx, CommandErrorType.PERMISSION)
                            return
                    except ValueError:
                        #allow command to proceed if no permission is created
                        return await func(*args, **kwargs)

                # Check if command is enabled
                if not command.enabled:
                    await send_error(ctx, CommandErrorType.DISABLED)
                    return

                # Get user's roles
                user_roles = [role.name for role in ctx.author.roles]

                # check role permissions
                if command.permissions["enabled_roles"]:
                    if not any(role in command.permissions["enabled_roles"] for role in user_roles):
                        await send_error(
                            ctx,
                            CommandErrorType.ROLE_REQUIRED,
                            ', '.join(command.permissions['enabled_roles'])
                        )
                        return

                if command.permissions["disabled_roles"]:
                    if any(role in command.permissions["disabled_roles"] for role in user_roles):
                        await send_error(
                            ctx,
                            CommandErrorType.ROLE_BLOCKED,
                            ', '.join(command.permissions['disabled_roles'])
                        )
                        return

                # check channel permissions
                if command.permissions["allowed_channels"]:
                    if ctx.channel.name not in command.permissions["allowed_channels"]:
                        await send_error(
                            ctx,
                            CommandErrorType.CHANNEL_ALLOWED,
                            ', '.join(command.permissions['allowed_channels'])
                        )
                        return

                if command.permissions["disabled_channels"]:
                    if ctx.channel.name in command.permissions["disabled_channels"]:
                        await send_error(
                            ctx,
                            CommandErrorType.CHANNEL_BLOCKED,
                            ', '.join(command.permissions['disabled_channels'])
                        )
                        return

                return await func(*args, **kwargs)
            except Exception as e:
                # check for errors
                print(f"Permission check error for {command_name}: {str(e)}")
                await send_error(ctx, CommandErrorType.PERMISSION)
                return
        return wrapper
    return decorator

# Example usage:
"""
@commands.command(name="ban")
@check_command_permissions("ban")
async def ban(self, ctx, member: discord.Member, *, reason: str = None):
    # Command implementation here
    pass
"""
