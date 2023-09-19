import discord
from discord.ext import commands

import pytube as pt

import os
import Config as cn
import Logs as logs
import random

import asyncio

class music_cog(commands.Cog):


    def __init__(self,bot):
        self.bot = bot

        self.music_clients = {}
        self.first_command = True

        for guild in bot.guilds:
            
            self.music_clients[guild] = music_client(bot)

    def update_cogs(self):
        if self.first_command:
            for guild in self.bot.guilds:
                self.music_clients[guild] = music_client(self.bot)
            self.first_command = False

    @commands.command(name="play",aliases=["p","з"],help="play the selected song from youtube")
    async def play(self, ctx, *args):
        self.update_cogs()

        await self.music_clients[ctx.guild].play(ctx, *args)
    @commands.command(name="PLAY",aliases=["pm","зь"],help="play the selected song from youtube X times")
    async def PLAYultytime(self, ctx, *args):
        self.update_cogs()

        await self.music_clients[ctx.guild].PLAYultytime(ctx, *args)
    @commands.command(name = "pause",aliases = ["pa","зф"], help = "pause the current song")
    async def pause(self,ctx,*args):
        self.update_cogs()

        await self.music_clients[ctx.guild].pause(ctx) 
    @commands.command(name = "resume",aliases = ["r","к"], help = "resume the current song")
    async def resume(self,ctx,*args):
        self.update_cogs()
        await self.music_clients[ctx.guild].resume()
    @commands.command(name = "skip",aliases = ["s","ы"], help = "skip the current song")
    async def skip(self,ctx):
        self.update_cogs()

        await self.music_clients[ctx.guild].skip(ctx)
    @commands.command(name = "queue",aliases = ["q","й"], help = "shows queue")
    async def queue(self,ctx):
        self.update_cogs()

        await self.music_clients[ctx.guild].queue(ctx)    
    @commands.command(name = "clear",aliases = ["c","с"], help = "clear queue")
    async def clear(self,ctx):
        self.update_cogs()

        await self.music_clients[ctx.guild].clear(ctx)
    @commands.command(name = "leave",aliases = ["l","д"], help = "Disconnect bot from channel")
    async def leave(self,ctx):
        self.update_cogs()

        await self.music_clients[ctx.guild].leave()

  
        

class cache():
    def __init__(self):
        self.Cache = {}

    def check(self,key):

        logs.add_log('i','[DF][CHECK] Check called')
        try:
            var = self.Cache[key]
            return var
        except Exception as e:
            logs.add_log('w',f'[DF][CHECK] {e}')
            return None
    def add(self,key,value):
        logs.add_log('i','[DF][ADD] Add called')
        self.Cache[key]=value
 

        



class music_client():
    def __init__(self,bot):
        self.bot = bot 
        self.cache = cache()
        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.YDL_OPTIONS = {"format":"bestaudio/best","noplaylist":"True",'quiet': True}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

        self.path = cn.bot_path
        self.special_char = [';', '!', ':', '@', "*", '%', '^','!',"|"]


        self.vc = None
    def pick_rnd(self, str):
        return str[random.randint(0,len(str)-1)]
   
    
    def download(self,item):
        video = item
        
        title = video.title
        for i in self.special_char:
            title = title.replace(i,"").lower()

        if not os.path.exists(self.path+title.lower()+"1.mp3"):
            logs.add_log('i', "[DF][DN] downloading - "+title+"1.mp3")
            audio = video.streams.filter(only_audio=True).first().download(filename=title.lower()+"1.mp3")

        else:
            logs.add_log('g', "[DF][DN] downloading skipped -> track already downloaded")

        return title+"1.mp3"

    

    def search_yt(self,item):
        title = ""

        cache_check = self.cache.check(item)

        if os.path.exists(self.path + item.lower() + "1.mp3"):
            logs.add_log('g', "[DF][SY] File finden in path using name")
            return {'source' : '','title' : item.lower()+"1.mp3"}
        
        if cache_check != None:
            if os.path.exists(self.path + cache_check):
                logs.add_log('g', "[DF][SY] File finden in path using cache")
                return {'source' : '','title': cache_check}
            

        else:
            logs.add_log('w', "[DF][SY] File not finden in path")

            try:
                if "https://" in item:
                    title = self.download(pt.YouTube(item))
                    self.cache.add(item,title)

                else:
                    title = self.download(pt.Search(item).results[0])
                    self.cache.add(item,title)

            except Exception as e:
                logs.add_log('w', "[SY] Song dont downloaded " + str(e))
                return False
            
            logs.add_log('i', "[DF][SY] Song is ready - "+title)
            return {'source':"",'title':title}
            
    def play_next(self,ctx):
        logs.add_log('i', "[DF][PN] play_next called")

        if len(self.music_queue)>0:
            if self.vc == None or not self.vc.is_connected():
                logs.add_log('i', "[DF][PN] Bot not connected to voice_channel")
                self.is_playing = False
                self.is_paused = False
                return
            
            m_url = self.music_queue[0][0]['title']
            self.music_queue.pop(0)

            logs.add_log('i', "[DF][PN] "+m_url+" is playing")

            var = discord.FFmpegPCMAudio(source=m_url,executable=cn.ffmpeg_path)
            self.is_playing = True
            self.vc.play(var,after=lambda e: self.play_next(ctx))

        else:
            logs.add_log('i', "[DF][PN] Run out of queue")
            self.is_playing = False
            self.is_paused = False




    async def play_music(self,ctx):
        logs.add_log('i', "[DF][PM] play_music called")

        if len(self.music_queue) > 0:

            if self.vc == None or not self.vc.is_connected():   

                logs.add_log('i', "[DF][PM] Trying to connect to the voice channel")
                self.vc = await self.music_queue[0][1].connect()

            else:

                await self.vc.disconnect()
                self.vc = await self.music_queue[0][1].connect()
                logs.add_log('i', "[DF][PM] moved to another voice channel")

            if self.vc == None:

                await ctx.send(self.pick_rnd(cn.cant_connect_to_vc))
                await self.clear(ctx)
                logs.add_log('e', "[DF][PM] Could not connect to the voice channel")
                self.is_playing = False
                self.is_paused = False
                return   

            m_url = self.music_queue[0][0]['title']
            self.music_queue.pop(0)

            logs.add_log('i', f"[DF][PM] Title: {m_url} is playing")

            var = discord.FFmpegPCMAudio(source=m_url,executable=cn.ffmpeg_path)
            self.is_playing = True
            self.vc.play(var,after=lambda e: self.play_next(ctx))
        else:
            logs.add_log('i', "[DF][PM] Run out of queue")
            self.is_playing = False
            self.is_paused = False

    async def play(self, ctx, *args):
        logs.add_log('i', "[CM][PLAY] play called")

        query = " ".join(args)
        voice_channel = ctx.author.voice.channel

        if ctx.author.voice is None or ctx.author.voice.channel == None:
            logs.add_log('e', "[CM][PLAY] User not in voice")
            await ctx.send(self.pick_rnd(cn.user_not_in_vc))
            return


        if query == "":

            logs.add_log('w', "[CM][PLAY] called without *args ")
            if self.is_paused:

                self.vc.resume()
            elif self.is_playing == False and self.music_queue.count != 0:

                await self.play_music(ctx)     
            else:

                logs.add_log('w', "[CM][PLAY] without *args unsuccessful")          
        else:

            logs.add_log('i', f"[CM][PLAY] called with *args - {query}")
            await ctx.send(self.pick_rnd(cn.searching_song))

            repeat = 1
            if 'x ' in query:

                logs.add_log('i',f"[CM][PLAY] Play used for {repeat} repeats")
                query = query.split("x ") 
                repeat = int(query[0])
                query = query[1]

            if self.vc == None or not self.vc.is_connected():

                logs.add_log('w', "[CM][PM] Bot not connected to voice channel")
                self.is_playing = False
                self.is_paused = False  

            if self.is_playing == False and self.is_paused == False:

                    logs.add_log('i', "[CM][PLAY] self.is_playing == False and self.is_paused == False")
                
                

                    song = self.search_yt(query)
                    if(type(song) == type(True)):

                        logs.add_log('e', "[CM][PLAY] song == False")
                        await ctx.send(self.pick_rnd(cn.cant_download_song))
                    else:

                        await ctx.send(song['title'].replace("1.mp3","") + self.pick_rnd(cn.song_added_to_queue))
                        
                        if(type(repeat)==type(1)):

                            for i in range(repeat):
                                self.music_queue.append([song,voice_channel]) 
                            logs.add_log('i', "[DF][PM] QUEUE LEN = "+str(len(self.music_queue)))     
                        else: 

                            self.music_queue.append([song,voice_channel])
                        
                        await self.play_music(ctx)
                        
            else:
                logs.add_log('i', "[CM][PLAY] self.is_playing != False or self.is_paused != False")
                song = self.search_yt(query)

                if(type(song) == type(True)):
                    logs.add_log('e', "[CM][PLAY] song == False")
                    await ctx.send(self.pick_rnd(cn.cant_download_song))
                else:
                    for i in range(repeat):
                        self.music_queue.append([song,voice_channel]) 
                    logs.add_log('i', "[DF][PM] QUEUE LEN = "+str(len(self.music_queue)))
                    await ctx.send(song['title'].replace("1.mp3","") + self.pick_rnd(cn.song_added_to_queue))


    async def pause(self,ctx):
        logs.add_log('i', "[CM][Pause] pause called")
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            await ctx.send(self.pick_rnd(cn.paused))
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            await ctx.send(self.pick_rnd(cn.resumed))
    async def resume(self):
        logs.add_log('i', "[CM][Resume] resume called")
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
    async def skip(self,ctx):
        logs.add_log('i', "[CM][Skip] skip called")
        if self.vc != None and self.is_playing:
            self.vc.stop()
            await self.play_music(ctx)
    async def queue(self,ctx):
        logs.add_log('i', "[CM][Queue] queue called")
        retval = ""

        for i in range(0, len(self.music_queue)):
            if i > 4: 
                retval+="...\n"
                break
            retval += str(i)+". "+self.music_queue[i][0]['title'].replace("1.mp3","") + '\n'
        
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send(self.pick_rnd(cn.queue_empty))
    async def clear(self,ctx):
        logs.add_log('i', "[CM][Clear] clear called")

        self.vc.stop()
        self.music_queue = []
        await ctx.send(self.pick_rnd(cn.queue_cleared))

    async def leave(self):
        logs.add_log('i', "[CM][Leave] leave called")
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()


                

