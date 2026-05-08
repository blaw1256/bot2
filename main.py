import discord
from discord.ext import commands
import logging 
import os
import webserver
from dotenv import load_dotenv
import asyncio
import math
import sheets

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


mainshop = []

items = sheets.get_all_values()
for item in items:
    if item == ['name', 'price', 'desc', 'id', '', '']:
        continue
    else:
        item = {'name':item[0], 'price': item[1], 'id':item[3], 'desc':item[2]}
        mainshop.append(item)

length = len(mainshop)

@bot.event
async def on_ready():
    #sheets.add_shop() 
    print("WARPS Shop Bot is now running.") 
 


@bot.command()
async def shop(ctx):

    mainshop = []

    items = sheets.get_all_values()
    for item in items:
        if item == ['name', 'price', 'desc', 'id']:
            continue
        else:
            item = {'name':item[0], 'price': item[1], 'id':item[3], 'desc':item[2]}
            mainshop.append(item)

     #f = open('shop.txt','r')  
    # for line in f:
    #     line = line.strip()
    #     line = line.split(' , ')                                                          
    #     line[2] = line[2].replace('\\n','\n')                                             LEGACY CODE, IGNORE
    #     item = {'name':line[0],'price':line[1],'desc':line[2]}
    #     mainshop.append(item)
    #f.close()

    global length
    length = len(mainshop)
    emlist=[]
    cur_page = 0
    pages = math.ceil(len(mainshop)/10)

    for index in range(pages):
        em=discord.Embed(title='Shop', type='article')
        emlist.append(em)

    for index,item in enumerate(mainshop):
        page = math.floor(index/10)
        em = emlist[page]
        name = item['name']
        price = item['price']
        desc = item['desc']
        id = item['id']
        em.add_field(name=name, value=f"Price: {price} \n Shop ID: {id} \n Description: \n{desc}", inline=False)
    # making the embed pages for the shop

    message =  await ctx.send(content=f"Page {cur_page+1}/{pages}:", embed=emlist[0])
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")
    #adding reactions to change pages

    def check(reaction, user):
        return str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(embed=emlist[cur_page],content=f"Page {cur_page+1}/{pages}:")
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 0:
                cur_page -= 1
                await message.edit(embed=emlist[cur_page],content=f"Page {cur_page+1}/{pages}:")
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            print("no")
        #     break
            # ending the loop if user doesn't react after x seconds

@bot.command()
async def sell(ctx):
    auth = ctx.author
    def check(m):
        return m.author == auth
    await auth.send('name')
    name2 = await bot.wait_for('message', check=check)
    name = name2.content
    await auth.send('Price:')
    price2 = await bot.wait_for('message', check=check)
    price = price2.content
    await auth.send(f'desc')
    desc2 = await bot.wait_for('message', check=check)
    desc = desc2.content
    await auth.send(f"{name}, {int(price)}, {desc}")
    item = [name,price,desc]
    #getting the info of the item
 

    sheets.add_item(length,item)
    # f = open('shop.txt','a')
    # f.write('\n')
    # f.write(f"{name} , {2*int(price)} , {desc}")              LEGACY CODE
    # f.close()
    # sheets.add_shop()
    await auth.send("Done!")
    await ctx.send("Item Added to Shop")
    #adding to 
    

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)