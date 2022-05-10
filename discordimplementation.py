 # bot.py
from random import randrange
import discord
from discord.ext import commands # This is just an extension to make commands a lot easier
import requests
import math
import random
import json


bot = commands.Bot(command_prefix=".", help_command=None)


@bot.event
async def on_ready(): 
    print("Logged in successfuly as " + bot.user.name)

@bot.command() 
async def isOnline(ctx):
    await ctx.send("I am online !")

@bot.command(aliases=['fuckinghelpme', 'help'])
async def Help(ctx):
    embed1=discord.Embed(
        title="Help Page",
        color=discord.Color.blue())
   
    embed1.add_field(name=".isOnline", value="Sends a message if the bot is online.", inline=False)
    embed1.add_field(name=".Help", value="I think you can figure out this one by yourself.", inline=False)
    embed1.add_field(name=".under25k", value="Returns a list of non exempted members under 25k", inline=False)
    embed1.add_field(name=".ListAdd", value="Adds the UUID of a player to the GXP exemption list", inline=False)
    await ctx.send(embed=embed1)

@bot.command()
async def under25k(ctx):
    g = requests.get("https://api.hypixel.net/guild?key=" + APILIST[1] + "&name=Hypixel+Knights")
    g = g.json()
    UnderReqList = []
    GxpList = []
    for i in range(len(g['guild']['members'])):
        #Get member name, Hypixel API only gives UUIDs
        uuid = g['guild']['members'][i]['uuid']

        x = requests.get("https://playerdb.co/api/player/minecraft/" + uuid)
        x = x.json()
        uname = x['data']['player']['username']
        expHistory = expHistory = g['guild']['members'][i]['expHistory']
        expHistory = sum(expHistory.values())
        if (int(expHistory) >= 0 and int(expHistory) < 25000):
            UnderReqList.append(uname)
            GxpList.append(expHistory)
    #Send msg         
    embedgxp=discord.Embed(
        title="List of people under 25k GXP",
        color=discord.Color.dark_gold()
    ) 
    j = 0
    SpecialExempts = []
    for line in open ('safelist.txt', 'r').readlines():
        SpecialExempts.append(line.strip())
    for i in UnderReqList:
        j+=1
        x = requests.get("https://playerdb.co/api/player/minecraft/" + i)
        x = x.json()
        PLAYER_UUID = x['data']['player']['raw_id']
        if (j % 25 != 0 and j<25 and PLAYER_UUID not in SpecialExempts): # Add check Hono/Insurance
            embedgxp.add_field(name=i, value="**➤ GXP:** `"+ str(GxpList[UnderReqList.index(i)]) +"`", inline=False)
        else:
            if (j % 25 == 0):
                await ctx.send(embed=embedgxp)
                embedgxp=discord.Embed(
                    title="List of people under 25k GXP",
                    color=discord.Color.dark_gold()
                ) 
        if (j > 25 and (j % 25 !=0) and PLAYER_UUID not in SpecialExempts): #Add check Hono/Insurance
            embedgxp.add_field(name=i, value="**➤ GXP:** `"+ str(GxpList[UnderReqList.index(i)]) +"`", inline=False)    
    await ctx.send(embed=embedgxp)

@bot.command()
async def ListAdd(ctx, P_UUID):
    ErrorFind = False
    x = requests.get("https://playerdb.co/api/player/minecraft/" + P_UUID)
    x = x.json()
    if x.get('error') == True:
        await ctx.send("I was unable to find the player.")
        ErrorFind = True
    
    #add to txt
    if (ErrorFind == False):
        PeopleTXT = open('safelist.txt', 'a')
        PeopleTXT.write(str(P_UUID) + "\n")
        PeopleTXT.close
        await ctx.send("The player has been added to the list")

    

# Local file containing the API key
APILIST = []
for line in open("c:\\python\\API.txt", "r").readlines():
    APILIST.append(line.strip())



# This just runs our bot using a local file containing the API key.
bot.run(APILIST[0]) 

#TODO LIST :
#COMMAND TO REMOVE POEPLE FROM LIST