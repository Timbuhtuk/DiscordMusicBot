import discord
from discord.ext import commands
import Config as cn

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
    
    async def send_to_all(self,msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)

    @commands.command(name = "help",aliases = ["h",'VLADlox'], help = "help")
    async def help(self,ctx):
        print("[INF][CM][Help] help CALLED")
        await ctx.send(self.help_message)
    
    @commands.command(name="test",aliases=["t"],help="")
    async def test(self, ctx, *args):
        vc = await ctx.author.voice.channel.connect()
