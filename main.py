import discord
from discord.ext import commands

import os
import asyncio

from music_cog import music_cog_arr
from music_cog import music_cog
from help_cog import help_cog
import Config

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=Config.command_tag,intents=intents,help_command=None)
Ready = False


async def setup():
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog_arr(bot))
    print(bot.cogs)
    await bot.start(Config.token)


asyncio.run(setup())


 
