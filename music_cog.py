import discord
from discord.ext import commands

from yt_dlp import YoutubeDL as YDL
from pytube import YouTube

import os
import Config as cn
import random
from datetime import datetime

class music_cog_arr(commands.Cog):


    def __init__(self,bot):
        self.bot = bot

        self.music_cogs = {}
        self.first_command = True

        for guild in bot.guilds:
            
            self.music_cogs[guild] = music_cog(bot)

    def update_cogs(self):
        if self.first_command:
            for guild in self.bot.guilds:
                self.music_cogs[guild] = music_cog(self.bot)
            self.first_command = False

    @commands.command(name="play",aliases=["p","з"],help="play the selected song from youtube")
    async def play(self, ctx, *args):
        self.update_cogs()

        await self.music_cogs[ctx.guild].play(ctx, *args)
    @commands.command(name="playm",aliases=["pm","зь"],help="play the selected song from youtube X times")
    async def playmultytime(self, ctx, *args):
        self.update_cogs()

        await self.music_cogs[ctx.guild].playmultytime(ctx, *args)
    @commands.command(name = "pause",aliases = ["pa","зф"], help = "pause the current song")
    async def pause(self,ctx,*args):
        self.update_cogs()

        await self.music_cogs[ctx.guild].pause(ctx) 
    @commands.command(name = "resume",aliases = ["r","к"], help = "resume the current song")
    async def resume(self,ctx,*args):
        self.update_cogs()
        await self.music_cogs[ctx.guild].resume()
    @commands.command(name = "skip",aliases = ["s","ы"], help = "skip the current song")
    async def skip(self,ctx):
        self.update_cogs()

        await self.music_cogs[ctx.guild].skip(ctx)
    @commands.command(name = "queue",aliases = ["q","й"], help = "shows queue")
    async def queue(self,ctx):
        self.update_cogs()

        await self.music_cogs[ctx.guild].queue(ctx)    
    @commands.command(name = "clear",aliases = ["c","с"], help = "clear queue")
    async def clear(self,ctx):
        self.update_cogs()

        await self.music_cogs[ctx.guild].clear(ctx)
    @commands.command(name = "leave",aliases = ["l","д"], help = "Disconnect bot from channel")
    async def leave(self,ctx):
        self.update_cogs()

        await self.music_cogs[ctx.guild].leave()

  
        



class music_cog():
    def __init__(self,bot):
        self.bot = bot 

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.YDL_OPTIONS = {"format":"bestaudio/best","noplaylist":"True"}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

        self.path = cn.bot_path
        self.special_char = [';', '!', ':', '@', "*", '%', '^','!',"|"]


        self.vc = None
    def pick_rnd(self, str_arr):
        return str_arr[random.randint(0,len(str_arr)-1)]
    def add_log(self,str):
        if cn.music_cog_logging == True:
            time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            print('['+time+']'+str)    
    
    def download(self,item):
        video = YouTube(item)
        
        title = video.title
        for i in self.special_char:
            title = title.replace(i,"")

        if not os.path.exists(self.path+title+"1.mp3"):
            self.add_log("[INF][DF][DN] downloading - "+title+"1.mp3")
            audio = video.streams.filter(only_audio=True).first().download(filename=title+"1.mp3")
        else:
            self.add_log("[INF][DF][DN] downloading skipped -> track already downloaded")

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
                self.add_log("[INF][SY] Song dont downloaded " + str(e))
                return False
        
        self.add_log("[INF][DF][SY] Song is ready - "+title)
        return {'source':info['formats'][0]['url'],'title':title}
    def play_next(self,ctx):
        self.add_log("[INF][DF][PN] play_next CALLED")

        if len(self.music_queue)>0:
            if self.vc == None or not self.vc.is_connected():
                self.add_log("[INF][DF][PN] Bot not connected to voice_channel")
                self.is_playing = False
                self.is_paused = False
                return
            
            m_url = self.music_queue[0][0]['title']
            self.music_queue.pop(0)

            self.add_log("[INF][DF][PN]"+m_url+" is playing")

            var = discord.FFmpegPCMAudio(source=m_url,executable="C:\\ffmpeg\\ffmpeg.exe")
            self.is_playing = True
            self.vc.play(var,after=lambda e: self.play_next(ctx))

        else:
            self.add_log("[INF][DF][PN] Run out of queue")
            self.is_playing = False
            self.is_paused = False



    async def play_music(self,ctx):
        self.add_log("[INF][DF][PM] play_music CALLED")

        if len(self.music_queue) > 0:
            self.add_log("[INF][DF][PM] QUEUE LEN = "+str(len(self.music_queue)))

            if self.vc == None or not self.vc.is_connected():   

                self.add_log("[INF][DF][PM] Trying to connect to the voice channel")
                self.vc = await self.music_queue[0][1].connect()

            else:
                await self.vc.move_to(self.music_queue[0][1])
                self.add_log("[INF][DF][PM] moved to another voice channel")

            if self.vc == None:
                await ctx.send(self.pick_rnd(cn.cant_connect_to_vc_arr))
                await self.clear(ctx)
                self.add_log("[INF][DF][PM] Could not connect to the voice channel")
                self.is_playing = False
                self.is_paused = False
                return   
            

            
            

            m_url = self.music_queue[0][0]['title']
            self.music_queue.pop(0)

            self.add_log("[INF][DF][PM] Title: "+m_url+" is playing")

            var = discord.FFmpegPCMAudio(source=m_url,executable="C:\\ffmpeg\\ffmpeg.exe")
            self.is_playing = True
            self.vc.play(var,after=lambda e: self.play_next(ctx))
        else:
            self.add_log("[INF][DF][PM] Run out of queue")
            self.is_playing = False
            self.is_paused = False



    async def play(self, ctx, *args):
        self.add_log("[INF][CM][Play] play CALLED")

        query = " ".join(args)
        voice_channel = ctx.author.voice.channel


        self.add_log("[INF][CM][Play] with *args - "+query)
        await ctx.send(self.pick_rnd(cn.searching_song))

        if self.is_playing == False and self.is_paused == False:
            self.add_log("[INF][CM][Play] IF")
                
            if voice_channel is None:
                self.add_log("[INF][CM][Play] User not in voice")
                await ctx.send(self.pick_rnd(cn.user_not_in_vc_arr))
            else:
                song = self.search_yt(query)
                if(type(song) == type(True)):
                    self.add_log("[INF][CM][Play] song == False")
                    await ctx.send(self.pick_rnd(cn.cant_download_song_arr))
                else:
                    await ctx.send(song['title'].replace("1.mp3","") + self.pick_rnd(cn.song_added_to_queue_arr))

                    self.music_queue.append([song,voice_channel])
                        
                    await self.play_music(ctx)               
        else:
            self.add_log("[INF][CM][Play] ELSE")
            song = self.search_yt(query)

            if(type(song) == type(True)):
                self.add_log("[INF][CM][Play] song == False")
                await ctx.send(self.pick_rnd(cn.cant_download_song_arr))
            else:

                    self.music_queue.append([song,voice_channel])
                    await ctx.send(song['title'].replace("1.mp3","") + self.pick_rnd(cn.song_added_to_queue_arr))

    async def playmultytime(self, ctx, *args):
        self.add_log("[INF][CM][PlayM] playmultytime CALLED")

        query = " ".join(args)
        voice_channel = ctx.author.voice.channel

        if query == "":
            self.add_log("[INF][CM][PlayM] without *args ")
            if self.is_paused:
                self.vc.resume()
            elif self.is_playing == False:
                await self.play_music(ctx)               
        else:
            self.add_log("[INF][CM][PlayM] with *args - "+query)
            await ctx.send(self.pick_rnd(cn.searching_song))

            query = query.split("x ") 
            repeat = int(query[0])
            query = query[1]
            
            

            if self.is_playing == False and self.is_paused == False:
                self.add_log("[INF][CM][PlayM] IF")
                
                if voice_channel is None:
                    self.add_log("[INF][CM][PlayM] User not in voice")
                    await ctx.send(self.pick_rnd(cn.user_not_in_vc_arr))
                else:
                    song = self.search_yt(query)
                    if(type(song) == type(True)):
                        self.add_log("[INF][CM][PlayM] song == False")
                        await ctx.send(self.pick_rnd(cn.cant_download_song_arr))
                    else:
                        await ctx.send(song['title'].replace("1.mp3","") + self.pick_rnd(cn.song_added_to_queue_arr))
                        
                        if(type(repeat)==type(1)):
                            for i in range(repeat):
                                self.music_queue.append([song,voice_channel])      
                        else: 
                            self.music_queue.append([song,voice_channel])
                        
                        await self.play_music(ctx)
                        
            else:
                self.add_log("[INF][CM][PlayM] ELSE")
                song = self.search_yt(query)

                if(type(song) == type(True)):
                    self.add_log("[INF][CM][PlayM] song == False")
                    await ctx.send(self.pick_rnd(cn.cant_download_song_arr))
                else:

                    self.music_queue.append([song,voice_channel])
                    await ctx.send(song['title'].replace("1.mp3","") + self.pick_rnd(cn.song_added_to_queue_arr))



    async def pause(self,ctx):
        self.add_log("[INF][CM][Pause] pause CALLED")
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            await ctx.send(self.pick_rnd(cn.paused_arr))
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            await ctx.send(self.pick_rnd(cn.resumed_arr))
    async def resume(self):
        self.add_log("[INF][CM][Resume] resume CALLED")
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
    async def skip(self,ctx):
        self.add_log("[INF][CM][Skip] skip CALLED")
        if self.vc != None and self.is_playing:
            self.vc.stop()
            await self.play_music(ctx)
    async def queue(self,ctx):
        self.add_log("[INF][CM][Queue] queue CALLED")
        retval = ""

        for i in range(0, len(self.music_queue)):
            if i > 4: 
                retval+="...\n"
                break
            retval += str(i)+". "+self.music_queue[i][0]['title'].replace("1.mp3","") + '\n'
        
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send(self.pick_rnd(cn.queue_empty_arr))
    async def clear(self,ctx):
        self.add_log("[INF][CM][Clear] clear CALLED")

        self.vc.stop()
        self.music_queue = []
        await ctx.send(self.pick_rnd(cn.queue_cleared_arr))

    async def leave(self):
        self.add_log("[INF][CM][Leave] leave CALLED")
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name = "jacob")
    async def Test1(self,ctx):

        with YDL(self.YDL_OPTIONS) as ydl:
            
            info = ydl.extract_info(ctx.message.content.split(" ")[1], download = True)
                






        