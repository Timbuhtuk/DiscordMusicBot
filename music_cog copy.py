import discord
from discord.ext import commands

from yt_dlp import YoutubeDL as YDL
from pytube import YouTube

import os
import time

class music_cog():
    def __init__(self,bot):
        self.bot = bot 

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.YDL_OPTIONS = {'''"format":"bestaudio/best",'''"noplaylist":"True"}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

        self.path = "D:\\DiscordBot\\"
        self.special_char = [';', '!', ':', '@', "*", '%', '^','!',"|"]


        self.vc = None
    def download(self,item):
        video = YouTube(item)
        
        title = video.title
        for i in self.special_char:
            title = title.replace(i,"")

        if not os.path.exists(self.path+title+"1.mp3"):
            print("[INF][DF][DN] downloading - "+title+"1.mp3")
            audio = video.streams.filter(only_audio=True).first().download(filename=title+"1.mp3")
        else:
            print("[INF][DF][DN] downloading skipped -> track already downloaded")

        return title+"1.mp3"
    def search_yt(self,item):
        title = ""
        with YDL(self.YDL_OPTIONS) as ydl:
            try:
                if "https://" in item:
                    info = ydl.extract_info(item, download = False)
                    title = self.download(info['formats'][0]['url'])

                else:
                    info = ydl.extract_info(f"ytsearch:{item}", download = False)['entries'][0]
                    title = self.download(info['formats'][0]['url'])

            except Exception as e:
                print("[INF][SY] Song dont downloaded " + str(e))
                return False
        
        print("[INF][DF][SY] Song is ready - "+title)
        return {'source':info['formats'][0]['url'],'title':title}
    def play_next(self):
        print("[INF][DF][PN] play_next CALLED")

        if len(self.music_queue)>0:

            self.is_playing = True

            m_url = self.music_queue[0][0]['title']

            self.music_queue.pop(0)

            print("[INF][DF][PN]"+m_url+" is playing")
            var = discord.FFmpegPCMAudio(source=m_url,executable="C:\\ffmpeg\\ffmpeg.exe")
            self.vc.play(var,after=lambda e: self.play_next())

        else:
            print("[INF][DF][PN] Run out of queue")
            self.is_playing=False


    async def play_music(self,ctx):
        
        print("[INF][DF][PM] play_music CALLED")
        if len(self.music_queue) > 0:

            self.is_playing = True

            m_url = self.music_queue[0][0]['title']
  
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    print("[INF][DF][PM] Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
                print("[INF][DF][PM] moved to another voice channel")

            self.music_queue.pop(0)

            print("[INF][DF][PM] Title: "+m_url+" is playing")
            var = discord.FFmpegPCMAudio(source=m_url,executable="C:\\ffmpeg\\ffmpeg.exe")
            self.vc.play(var,after=lambda e: self.play_next())
        else:
            print("[INF][DF][PM] Run out of queue")
            self.is_playing = False

    @commands.command(name="play",aliases=["p",'vladlox','lovevlaD',"з"],help="play the selected song from youtube")
    async def play(self, ctx, *args):
        print("[INF][CM][Play] play CALLED")
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel

        if query == "":
            print("[INF][CM][Play] QUEUE LEN = "+str(len(self.music_queue)))
            if self.is_paused:
                self.vc.resume()
            elif self.is_playing == False:
                await self.play_music(ctx)            
            
        else:
            if self.is_playing == False and self.is_paused == False:
                print("[INF][CM][Play] IF")
                
                if voice_channel is None:
                    await ctx.send("Connect to a voice channel!")
                else:
                    song = self.search_yt(query)
                    if(type(song) == type(True)):
                        await ctx.send("Could not download the song.")
                    else:
                        await ctx.send(song['title'].replace("1.mp3","")+ " added to queue")
                        
                        self.music_queue.append([song,voice_channel])
                        print("[INF][CM][Play] QUEUE LEN = "+str(len(self.music_queue)))

                        await self.play_music(ctx)
            else:
                print("[INF][CM][Play] ELSE")
                song = self.search_yt(query)

                if(type(song) == type(True)):
                    await ctx.send("Could not download the song.")
                else:
                   
                    self.music_queue.append([song,voice_channel])
                    await ctx.send("Song sdded to queue")
                    print("[INF][CM][Play] QUEUE LEN = "+str(len(self.music_queue)))

    @commands.command(name = "pause",aliases = ["pa",'vladloh','lovevlad',"зф"], help = "pause the current song")
    async def pause(self,ctx,*args):
        print("[INF][CM][Pause] pause CALLED")
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
        
    @commands.command(name = "resume",aliases = ["r",'Vladloh','Lovevlad',"к"], help = "resume the current song")
    async def resume(self,ctx,*args):
        print("[INF][CM][Resume] resume CALLED")
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name = "skip",aliases = ["s",'VladLoh','LoveVlad',"ы"], help = "skip the current song")
    async def skip(self,ctx,*args):
        print("[INF][CM][Skip] skip CALLED")
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name = "queue",aliases = ["q",'VladLox','LoveVlaD',"й"], help = "shows queue")
    async def queue(self,ctx):
        print("[INF][CM][Queue]] queue CALLED")
        retval = ""

        for i in range(0, len(self.music_queue)):
            if i > 4: break
            retval += str(i)+". "+self.music_queue[i][0]['title'].replace("1.mp3","") + '\n'
        
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in the queue.")
    
    @commands.command(name = "clear",aliases = ["c",'vladLox','loveVlaD',"с"], help = "clear queue")
    async def clear(self,ctx):
        print("[INF][CM][Clear] clear CALLED")
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Queue cleared!")

    @commands.command(name = "leave",aliases = ["l","disconnect","d",'VLADLOH','LOVEVLAD',"д","в"], help = "Disconnect bot from channel")
    async def leave(self,ctx):
        print("[INF][CM][Leave] leave CALLED")
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name = "w")
    async def Test(self,ctx):
        vc = await ctx.message.author.voice.channel.connect()
        print(1)
        print("[INF] Connected: "+str(vc.is_connected()))
        var = discord.FFmpegPCMAudio(source="https://youtu.be/ddVUelwmXmI?t=155",executable="C:\\ffmpeg\\ffmpeg.exe")

        print(var.read())
        vc.play(var,after=lambda e: self.play_next())
        print(4)
   
    def T():
        print("wevgruihyefrujvrgeunybgteUHI*NUBBVRF")
   
    @commands.command(name = "j")
    async def Test1(self,ctx):

        with YDL(self.YDL_OPTIONS) as ydl:
            
            info = ydl.extract_info(ctx.message.content.split(" ")[1], download = True)
                






        