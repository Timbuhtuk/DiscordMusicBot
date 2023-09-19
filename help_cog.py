import discord
from discord.ext import commands
import Config as cn
import Logs as logs

class help_cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        self.help_message = cn.help_message
        self.text_channel_text = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)
        print(cn.ready)
        #await self.send_to_all(self.help_massage)
    

    async def get_oauth_url(self):
        try:
            data = await self.bot.application_info()
        except AttributeError:
            return False
        return discord.utils.oauth_url(data.id)

    async def send_to_all(self,msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)

    @commands.command(name = "help",aliases = ["h"], help = "help")
    async def help(self,ctx):
        logs.add_log('i',"[CM][Help] help CALLED")
        url = await self.get_oauth_url()
        await ctx.send(self.help_message+'\n```'+url+'```')

