import discord
from discord.ext import commands

import os
import asyncio

from help_cog import help_cog

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!',intents=intents,help_command=None)



async def setup():
    await bot.add_cog(help_cog(bot))
    await bot.start("Nzc4NjkwOTYzMDAyNDkwODkw.Gi398V.U1OQT2QUR5qCMGvQbrbKsm9imfxwXH8QYz5_pw")




    
asyncio.run(setup())
 

    

                
            





        