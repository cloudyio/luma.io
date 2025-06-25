import discord
from db.models.config import Config

async def get_prefix(guild_id: str) -> str:
    config = await Config.find_one({"_id": str(guild_id)})

    if config and config.prefix:
        return config.prefix
    return "!"

async def update_prefix(guild_id: str, new_prefix: str) -> str:
    config = await Config.find_one({"_id": str(guild_id)})

    if not config:
        config = Config(str(guild_id), prefix=new_prefix)
        await config.insert_one()
    else:
        config.prefix = new_prefix
        await config.update_one()

    return config.prefix

