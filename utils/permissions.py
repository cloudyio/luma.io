from functools import wraps
from typing import Optional, Callable, Any
from enum import Enum
import discord
from discord.ext import commands
from db.models.commands import Command

class CommandErrorType(Enum):
    PERMISSION = "You don't have permission to use this command."
    SETUP = "This command is not set up in this server."
    DISABLED = "This command is currently disabled."
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
        

def check_command_permissions(command_name: str):
    """
    decorator to check if a user has permission to use a command based on:
    - role permissions (enabled/disabled/ignored roles)
    - channel permissions (allowed/disabled channels)
    - developer only status
    - command enabled status
    - cooldown status
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(ctx: commands.Context, *args, **kwargs):
            # Get command from database
            command = await Command.find_by_name_and_guild(command_name, str(ctx.guild.id))
            if not command:
                try:
                    permission = DefaultPermissions.get_permission(command_name)
                    if ctx.author.has_permissions(permission):
                        return await func(ctx, *args, **kwargs)
                    else:
                        await send_error(ctx, CommandErrorType.PERMISSION)
                        return
                except ValueError:
                    await send_error(ctx, CommandErrorType.SETUP)
                    return

            # Check if command is enabled
            if not command.enabled:
                await send_error(ctx, CommandErrorType.DISABLED)
                return

            # Check developer only
            if command.developer_only and not await ctx.bot.is_owner(ctx.author):
                await send_error(ctx, CommandErrorType.DEVELOPER)
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

            # check cooldown
            if command.cooldown["seconds"] > 0:
                cooldown_key = f"{ctx.author.id}:{command_name}" if command.cooldown["per_user"] else command_name
                
                if hasattr(ctx.bot, '_cooldowns'):
                    if cooldown_key in ctx.bot._cooldowns:
                        remaining = ctx.bot._cooldowns[cooldown_key]
                        await send_error(ctx, CommandErrorType.COOLDOWN, remaining)
                        return

            return await func(ctx, *args, **kwargs)
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
