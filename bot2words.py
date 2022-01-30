
import os
import random
from dotenv import load_dotenv
import discord
from random import seed
from random import randint
import time
import asyncio

from discord.ext import commands

#nepomembno-----------------------
load_dotenv(".env")
TOKEN = os.getenv('DISCORD_TOKEN')
print(os.getenv('DISCORD_TOKEN'))
#nepomembno----------------------

# 2

bot = commands.Bot(command_prefix='-')
bot.remove_command("help")                              # Zamenjan z -pomoč
channels = ["796708748243501106", "745616936301494396"] # V prihodnosti ID-ji kanalov, da lahko deluje samo v nekaterih
channelset = frozenset(channels)                       
predlogi = []


# Prižig
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="-pomoč"))



# Prebere besede v dictionary.
besede_dict = {}
with open("besede.txt", encoding='utf-8') as fp: 
        Lines = fp.read().splitlines()
        n = len(Lines)
        for i in range(n):
            beseda_str = Lines[i]
            nemsko, slovensko = beseda_str.split(' : ', 1)
            besede_dict[nemsko] = slovensko

# Prebere trenutni leaderboard.
leaderboard_dict = {}
with open("leaderboard.txt", encoding='utf-8') as fp: 
    Lines = fp.read().splitlines()
    n = len(Lines)
    for i in range(n):
        linija = Lines[i]
        uporabnik_id, max_rezultat = linija.split(' : ', 1)
        uporabnik_id = int(uporabnik_id)
        leaderboard_dict[uporabnik_id] = int(max_rezultat)
#Funkcija za zapisat leaderboard_dict v leaderboard.txt
def zapis_leaderboarda(dict:leaderboard_dict):
    with open("leaderboard.txt", 'w', encoding='utf-8') as fp: 
        for tekmovalec in leaderboard_dict:
            fp.write(str(tekmovalec) + " : " + str(leaderboard_dict[tekmovalec]) + "\n")

            
# Help command, sledi vzorcu ostalih če dodajaš. 
@bot.command()
async def pomoč(ctx):
    embed = discord.Embed(title="Domen Bot Help", description = "vaš asistent - pri nemscini")
    embed.add_field(name="-beseda", value="Dobiš naključno besedo v slovenščini.", inline="False")
    embed.add_field(name="-kviz", value="Koliko besed zapored lahko zapišeš pravilno?", inline="False")
    embed.add_field(name="-lestvica", value="Najboljši rezultati kvizovcev", inline="False")
    embed.add_field(name="-file", value="Pošljem trenutni file vseh besed", inline="False")
    embed.add_field(name="-quote", value="Vržem ven naključno bučko", inline="False")
    embed.add_field(name="-predlog", value="Predlagaj spremembe (primer: -predlog popravi crkovanje univerza)", inline="False")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/745616936301494395/772791128264671242/Screenshot_2020-04-23_at_10.05.10.png")
    await ctx.send(embed=embed)

# Prošnja za besedo
@bot.command(name='beseda')
async def beseda(ctx):  
    nemsko = random.choice(list(besede_dict.keys()))
    slovensko = besede_dict[nemsko]
    sinonimi = nemsko.split(" / ")
    # Testiraj če ima sinonime
    if len(sinonimi)>1:
        ima_sinonime = True
    else: 
        ima_sinonime = False
    # Besede so ločene z ' : ' (poglej besede.txt)
    kviz = "Tvoja beseda je: **" + slovensko + "**. Imaš 30 sekund časa, preden povem odgovor."
    await ctx.send(kviz)
    
    # Testiranje pravilnosti:
    if ima_sinonime:
        await ctx.send("Opomba: je več možnih odgovorov.")
        def check(message):
            return True 
        try:
            ugib = await bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.channel.send("Timeout. Odgovor je " + nemsko + ".")
        if ugib.content in sinonimi:
            await ctx.channel.send("Pravilno!")
        else:
            await ctx.channel.send("Nepravilno. Odgovor je " + nemsko + ".") 
    else:
        def check(message):
            return True
        try:
            ugib = await bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.channel.send("Timeout. Odgovor je " + nemsko + ".")
        if (ugib.content == nemsko):
            await ctx.channel.send("Pravilno!")
        else:
            await ctx.channel.send("Nepravilno. Odgovor je " + nemsko + ".")
        

@bot.command(name='quote')
async def quote(ctx):
    with open("quotes.txt", encoding='utf-8') as fp: 
        Lines = fp.read().splitlines()
        n = len(Lines) # Za randomizer
        st_besede = randint(0, n)
        beseda_str = Lines[st_besede]
    await ctx.send("Quote " + str(st_besede) + "/" + str(n) + ": " + beseda_str)

# Za poslat celoten seznam
@bot.command(name='file')
async def file(ctx):
    await ctx.send(file=discord.File(r'besede.txt'))

@bot.command(name='kviz')
async def kviz(ctx):
    pravilno = True
    score = 0
    besede_kviz = besede_dict.copy()
    kvizovec_id = ctx.message.author.id
    kvizovec_mention = ctx.message.author.mention
    while pravilno:
        if len(besede_kviz)==0:
            await ctx.send("Čestitam, znaš vse besede!")
            break
        nemsko = random.choice(list(besede_kviz.keys()))
        slovensko = besede_kviz[nemsko]
        besede_kviz.pop(nemsko)
        sinonimi = nemsko.split(" / ")
        # Testiraj če ima sinonime
        if len(sinonimi)>1:
            ima_sinonime = True
        else: 
            ima_sinonime = False
        st_poskusa = score+1
        timeout = False
        povej = "Kviz za " + kvizovec_mention + ". Tvoja " + str(st_poskusa) + ". beseda je **" + slovensko + "**. Imaš 30 sekund."
        await ctx.send(povej)
        if ima_sinonime:
            opomba = "Opomba: je več možnih odgovorov."
            await ctx.send(opomba)
            def check(message):
                if message.author.id == kvizovec_id:
                    return True 
                else:
                    return False
            try:
                ugib = await bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                pravilno = False
                timeout = True
                await ctx.channel.send("Timeout. Odgovor je " + nemsko + ".")
                
            if ugib.content in sinonimi:
                await ctx.channel.send("Pravilno!")
                score += 1
            elif timeout==False:
                await ctx.channel.send("Nepravilno. Odgovor je " + nemsko + ".")
                pravilno = False 
        else:
            def check(message):
                if message.author.id == kvizovec_id:
                    return True 
                else:
                    return False
            try:
                ugib = await bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                pravilno = False
                timeout = True
                await ctx.channel.send("Timeout. Odgovor je " + nemsko + ".")
                
            if (ugib.content == nemsko):
                await ctx.channel.send("Pravilno!")
                score += 1
            elif timeout==False:
                await ctx.channel.send("Nepravilno. Odgovor je " + nemsko + ".")
                pravilno = False

    koncni_msg = kvizovec_mention + ", tvoj rezultat je: " + str(score) + "."
    # Zapis v leaderboard.
    if kvizovec_id in leaderboard_dict:
        if score>leaderboard_dict[kvizovec_id]:
            leaderboard_dict[kvizovec_id] = score
            zapis_leaderboarda(leaderboard_dict)
    else:
        leaderboard_dict.update({kvizovec_id: score})
        zapis_leaderboarda(leaderboard_dict)
    await ctx.send(koncni_msg)    


@bot.command(name='lestvica')
async def lestvica(ctx):
    embed = discord.Embed(title="Najboljši Nemci")
    i=1
    leaderboard_dict_sorted = sorted(leaderboard_dict, key=leaderboard_dict.get, reverse=True)
    for nemec in leaderboard_dict_sorted:
        user = await bot.fetch_user(nemec)
        embed.add_field(name=str(i) + ".", value=str(user)+ " : "+ " <:star2:812705464537448530> " + str(leaderboard_dict[nemec]), inline=False)
        i+=1
    await ctx.send(embed=embed)


@bot.command(name='predlog')
async def predlog(ctx, arg):
    predlogi.append(arg)
    with open("predlogi.txt", 'w', encoding='utf-8') as p:
        for predlog in predlogi:
            p.write(predlog + "\n")
    await ctx.send("Hvala za tvoj predlog!")
bot.run(TOKEN)

#
#   IDEJE ZA NAPREJ:
#   - besede po poglavjih
#   - sharepoint API
