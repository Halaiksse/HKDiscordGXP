 # bot.py
from random import randrange
import discord
from discord.ext import commands # This is just an extension to make commands a lot easier
import requests
import math
import random

#this function creates the embeds
def makeEmbed(title_input):
    embedtemp=discord.Embed(
        title=title_input,
        color=discord.Color.dark_gold()
        ) 
    return embedtemp
#This function gets the JSON for player data, i'm mostly using this for rawid / ign translations.
def getPlayerData(input_uuid_or_ign):
    x = requests.get("https://playerdb.co/api/player/minecraft/" + input_uuid_or_ign)
    x = x.json()
    return x

bot = commands.Bot(command_prefix=".", help_command=None)


@bot.event
async def on_ready(): 
    print("Logged in successfuly as " + bot.user.name)

@bot.command() 
async def isOnline(ctx):
    await ctx.send("I am online !")

@bot.command(aliases=['fuckinghelpme', 'help'])
async def Help(ctx):
    #creation of the .help page
    embed1 = makeEmbed("Help Page")
    embed1.add_field(name=".isOnline", value="Sends a message if the bot is online.", inline=False)
    embed1.add_field(name=".Help", value="I think you can figure out this one by yourself.", inline=False)
    embed1.add_field(name=".under25k", value="Returns a list of non exempted members under 25k (This command can take up to a minute to completely execute)", inline=False)
    embed1.add_field(name=".ListAdd", value="Adds the UUID of a player to the GXP exemption list (Input IGN or UUID)", inline=False)
    embed1.add_field(name=".ListRemove", value="Remove the UUID of a player from the GXP exemption list (Input IGN or UUID)", inline=False)
    embed1.add_field(name=".ListShow", value="Shows the GXP exemption list", inline=False)
    await ctx.send(embed=embed1)

@bot.command()
async def under25k(ctx):
    #Getting the HK api JSON.
    g = requests.get("https://api.hypixel.net/guild?key=" + APILIST[1] + "&name=Hypixel+Knights")
    g = g.json()
    UnderReqList = []
    GxpList = []
    #For loop to check if g members gxp is under 25k
    for i in range(len(g['guild']['members'])):
        #Get member name, GXP history and rank.
        uuid = g['guild']['members'][i]['uuid']
        x = getPlayerData(uuid)
        uname = x['data']['player']['username']
        expHistory = expHistory = g['guild']['members'][i]['expHistory']
        expHistory = sum(expHistory.values())
        player_rank = g['guild']['members'][i]['rank']
        ExemptList = ["Officer", "Manager", "Guild Master"]
        #If under 25k and not staff, added to the list. 
        if (int(expHistory) >= 0 and int(expHistory) < 25000 and player_rank not in ExemptList):
            UnderReqList.append(uname)
            GxpList.append(expHistory)
    #Initiate embed.       
    embedgxp = makeEmbed("List of people under 25k GXP")
    j = 0
    SpecialExempts = []
    #Getting safelist
    for line in open ('safelist.txt', 'r').readlines():
        SpecialExempts.append(line.strip())
    
    for i in UnderReqList:
        j+=1
        x = getPlayerData(i)
        PLAYER_UUID = x['data']['player']['raw_id']
        #If embed not full, add field
        if (j % 25 != 0 and j<25 and PLAYER_UUID not in SpecialExempts): # Checking if member is safelisted.
            embedgxp.add_field(name=i, value="**➤ GXP:** `"+ str(GxpList[UnderReqList.index(i)]) +"`", inline=False)
        else:
            if (j % 25 == 0): # If embed is full, make another one and send current one
                await ctx.send(embed=embedgxp)
                embedgxp = makeEmbed("List of people under 25k GXP")
        #add field if embed not full.
        if (j > 25 and (j % 25 !=0) and PLAYER_UUID not in SpecialExempts): # Checking if member is safelisted
            embedgxp.add_field(name=i, value="**➤ GXP:** `"+ str(GxpList[UnderReqList.index(i)]) +"`", inline=False)    
    await ctx.send(embed=embedgxp)

@bot.command()
async def ListAdd(ctx, P_UUID):
    ErrorFind = False
    PlayerIGN = False
    x = getPlayerData(P_UUID)
    #If IGN, set ign flag to true.
    if (x.get('success') == True and len(P_UUID) <= 16):
        #If ign, get UUID.
        PLAYER_UUID = x['data']['player']['raw_id']
        PlayerIGN = True
        

    #Check if format is valid & not ign
    if (len(P_UUID)!=32 and PlayerIGN == False):
        await ctx.send("UUID Format incorrect, try to enter the raw/trimmed UUID")
        ErrorFind = True
    #check if uuid exists    
    if (x.get('error') == True and ErrorFind == False):
        await ctx.send("I was unable to find the player.")
        ErrorFind = True
    #check if player is in safelist already
    InitList = open("safelist.txt", "r")
    currentplayers = InitList.readlines()
    InitList.close()
    for line in currentplayers:
        if line.strip("\n") == str(P_UUID):
            ErrorFind = True
            await ctx.send("Player is already in the list")

    #add to txt
    if (ErrorFind == False):
        #IF not IGN, set UUID to current UUID.
        if (PlayerIGN == False):
            PLAYER_UUID = P_UUID
        PeopleTXT = open('safelist.txt', 'a')
        PeopleTXT.write(str(PLAYER_UUID) + "\n")
        PeopleTXT.close
        await ctx.send("The player has been added to the list")

@bot.command()
async def ListRemove(ctx, P_UUID):
    IGNFound = False
    x = getPlayerData(P_UUID)
    #If IGN, get UUID, otherwise UUID is fine. (Filter already done in adding)
    if (x.get('success') == True and len(P_UUID) <= 16):
        PLAYER_UUID = x['data']['player']['raw_id']
    else:
        PLAYER_UUID = P_UUID

    InitList = open("safelist.txt", "r")
    currentplayers = InitList.readlines()
    InitList.close()
    
    Safelist = open("safelist.txt", "w")
    #Rewrite file, but dont rewrite the UUID to remove line.
    for line in currentplayers:
        if line.strip("\n") != str(PLAYER_UUID):
            Safelist.write(line)
        if line.strip("\n") == str(PLAYER_UUID):
            IGNFound = True
    Safelist.close()
    if IGNFound:
        await ctx.send("The player has been removed from the list")
    else:
        await ctx.send("Could not find the player in the list")




@bot.command()
async def ListShow(ctx):
    j = 0
    SpecialExempts = []
    for line in open ('safelist.txt', 'r').readlines():
        SpecialExempts.append(line.strip())
    
    embedlist = makeEmbed("Safelisted users")
    
    for member in SpecialExempts:
        j+=1
        x = getPlayerData(member)
        uname = x['data']['player']['username'] # Get IGN with UUID in safelist.

        #If embed not full, add field
        if (j % 25 != 0 and j<25): 
            embedlist.add_field(name=member, value="**➤ IGN: ** `"+ uname +"`", inline=False) # IGN/UUID correspondance
        #if embed full, make another one
        else:
            if (j % 25 == 0):
                await ctx.send(embed=embedlist)
                embedlist = makeEmbed("Safelisted users")
        if (j > 25 and (j % 25 !=0)): 
            embedlist.add_field(name=member, value="**➤ IGN: ** `"+ uname +"`", inline=False)    # IGN/UUID correspondance
    await ctx.send(embed=embedlist)



# Local file containing the API key
APILIST = []
for line in open("c:\\python\\API.txt", "r").readlines():
    APILIST.append(line.strip())
# This just runs our bot using a local file containing the API key.
bot.run(APILIST[0]) 
