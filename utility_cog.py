import discord
from discord.ext import commands

import Config as cn
import random
from datetime import datetime


import json

class utility_cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot 


    def pick_rnd(self, str_arr):
        return str_arr[random.randint(0,len(str_arr)-1)]
    def add_log(self,str):
        if cn.utility_cog_logging == True:
            time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            print('['+time+']'+str)    

    @commands.command(name="flip",aliases=["f","а"],help="return True or False")
    async def flip(self,ctx):
        self.add_log("[INF][CM][Flip] flip CALLED")
        res = random.randint(0,1)
        if(res == 0):
            res = "False"
        else:
            res = "True"
        await ctx.send(self.pick_rnd(cn.flip)+res)
    @commands.command(name="random",aliases=["rnd","ктв"],help="return random int between 0 and X")
    async def rnd(self,ctx,*args):
        self.add_log("[INF][CM][Random] rnd CALLED")
        res = 0
        try:
            res = random.randint(0,int(args[0])) 
            await ctx.send(self.pick_rnd(cn.flip)+str(res)) 
        except:
            await ctx.send(self.pick_rnd(cn.flip)+str(random.randint(0,100)))
            self.add_log("[ERR][CM][Random] rnd get wrong argument: Type error")
            return
    
    
 
        self.add_log("[INF][CM][Delplayer] delplayer CALLED")

        data = {}
        file = open('data.txt','r')
        text = file.read()
        file.close()

        if text != "":
            data = json.loads(text)
        
        try:
            del data[ctx.message.author.global_name]
        except Exception as e:  
            print("[ERR][CM][Addplayer]"+str(e))
            return


        file = open('data.txt','w')
        file.write(json.dumps(data,indent=2))
        file.close()
        await ctx.send(self.pick_rnd(cn.user_dotaid_deleted))
        

        
    


 



        




