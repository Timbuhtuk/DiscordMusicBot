import discord
from discord.ext import commands

import asyncio

from music_cog import music_cog_arr
from help_cog import help_cog
import Config

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=Config.command_tag,intents=intents,help_command=None)


async def setup():
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog_arr(bot))
    print(bot.cogs)
    await bot.start(Config.token)

discord.utils.setup_logging()
asyncio.run(setup())


 
