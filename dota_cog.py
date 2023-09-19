
import discord
from discord.ext import commands

import Config as cn
import random
from datetime import datetime
import asyncio
import json
import requests

class dota_cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot 


    def pick_rnd(self, str_arr):
        return str_arr[random.randint(0,len(str_arr)-1)]
    def add_log(self,str):
        if cn.utility_cog_logging == True:
            time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            print('['+time+']'+str)    

    
    
    
    
    @commands.command(name="roshan_timing",aliases=["rt","ке"],help="remind to check roshpit")
    async def roshan_timing(self,ctx):
        self.add_log("[INF][CM][Roshantiming] roshantiming CALLED")
        await ctx.send(self.pick_rnd(cn.roshantiming_start))
        await asyncio.sleep(480)
        await ctx.send(self.pick_rnd(cn.roshantiming_end))
    
    @commands.command(name="add_player",aliases=["add_p","фввз"],help="adding player to database")
    async def add_player(self,ctx,*args):
        self.add_log("[INF][CM][Addplayer] addplayer CALLED")

        data = {}
        file = open('data.txt','r')
        text = file.read()
        file.close()

        if text != "":
            data = json.loads(text)
            
        data[ctx.message.author.global_name] = args[0]

        file = open('data.txt','w')
        file.write(json.dumps(data,indent=2))
        file.close()
        await ctx.send(self.pick_rnd(cn.user_dotaid_added))
    @commands.command(name="del_player",aliases=["del_p","вудз"],help="removing player from database")
    async def del_player(self,ctx):
        self.add_log("[INF][CM][Delplayer] delplayer CALLED")

        data = {}
        file = open('data.txt','r')
        text = file.read()
        file.close()

        if text != "":
            data = json.loads(text)
        else:
            return
        
        try:
            del data[ctx.message.author.global_name]
        except Exception as e:  
            print("[ERR][CM][Addplayer]"+str(e))
            return


        file = open('data.txt','w')
        file.write(json.dumps(data,indent=2))
        file.close()
        await ctx.send(self.pick_rnd(cn.user_dotaid_deleted))

    @commands.command(name="dota_top",aliases=["вщеф_ещз"],help="show player ranking top")
    async def dota_top(self,ctx):
        self.add_log("[INF][CM][Dota_top] dota_top CALLED")
        data = {}
        file = open('data.txt','r')
        text = file.read()
        file.close()
        
        
        r = requests.get("https://www.opendota.com/players/894825591")

        print()
        try:
            j = r.json()
        except Exception as e:
            print(e)

        '''if text != "":
            data = json.loads(text)
        else:
            return
        
       
            
        

        for player in data:
            print(data[player])
            
            jsontext = json.loads(r.json())'''
            
           

        
        


        

        
