import discord
import os
import logging
from db.connection import test_connection
from discord.ext import commands
from config import TOKEN, ENVIRONMENT
import discord
import jishaku

if ENVIRONMENT == 'production':
    level = logging.WARNING
else:
    level= logging.INFO

logging.basicConfig(
    level=level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.messages = True
        if ENVIRONMENT != 'production':
            intents.guilds = True

        super().__init__(command_prefix=self.get_prefix, intents=intents)

    async def get_prefix(self, message):
        default_prefix = os.getenv('DEFAULT_PREFIX', '!')

        if message.guild is None:
            return default_prefix

        from utils import utilities
        try:
            prefix = await utilities.get_prefix(str(message.guild.id))
            return [prefix, default_prefix]
        except Exception as e:
            logger.error(f"Error getting prefix: {e}")
            return default_prefix

    async def on_ready(self):
        logger.warning(f'Logged in as {self.user} (ID: {self.user.id}) PROD ENVIRONMENT')
        logger.warning('------')

    if ENVIRONMENT != 'production':
        from cogwatch import watch
        @watch(path='cogs', preload=True)
        async def on_ready(self):
            logger.info(f'Logged in as {self.user} (ID: {self.user.id}) DEV ENVIRONMENT')
            logger.info('------')


    async def setup_hook(self):
        await test_connection()
        await self.load_cogs()


    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f'Loaded cog: {filename}')
                except Exception as e:
                    logger.error(f'Failed to load cog {filename}: {e}')

        await self.load_extension('jishaku')


async def main():
    bot = Bot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())