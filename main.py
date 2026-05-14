import discord
from discord import app_commands
import logging 
import os
import webserver
from dotenv import load_dotenv
import math
import sheets
import asyncio


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
MY_GUILD = discord.Object(id=os.getenv('DB_GUILD_ID'))

mainshop = {}
count = 0

items = sheets.get_all_values()
for item in items:
    item = {'name':item[0], 'price': item[1], 'id':item[3], 'desc':item[2], 'stock':item[4], 'tier':int(item[5])}
    tier = item['tier']
    if tier in mainshop.keys():
        mainshop[tier].append(item)
        count+=1
    else:
        mainshop[tier] = []
        mainshop[tier].append({'name': f'Tier {tier}'})
        mainshop[tier].append(item)
        count +=2

global length
length = count - len(mainshop.keys())



#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyClient(discord.Client):
    # Suppress error on the User attribute being None since it fills up later
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
bot = MyClient(intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


# @bot.tree.command()
# async def hello(interaction: discord.Interaction):
#     """Says hello!"""
#     await interaction.channel.send(f'Hi, {interaction.user.mention}')

@bot.tree.command()
async def buy(interaction: discord.Interaction, item_name:str, amount:int):
    message = item_name
    #do it based off name
    message = message.lower()
    cell = sheets.string_find(message)
    # print(cell)
    # print(cell)
    # print(cell.col)
    # print(cell.value)
    # print(cell.row)
    if cell != None:
        outcome = sheets.stock_reduce(cell,amount)
        if outcome == ' stock error':
            await interaction.response.send_message('Failed: Tried to buy more than there is in stock.',ephemeral=True)
        elif outcome == 'tier error':
            await interaction.response.send_message('Item not found.', ephemeral=True)
        else:
            sheets.update_ids()
            await interaction.response.send_message('Transaction successful.', ephemeral=True)
            await interaction.channel.send(f'Sold {cell.value} X {amount} to {interaction.user.mention}!')
    else:
        await interaction.response.send_message('Item not found.',ephemeral=True)

    # sheets.update_ids()
    # await interaction.channel.send('Sold!')




@bot.tree.command()
async def sell(interaction, name:str, price:int, desc:str, stock:str):
    item = name,price,desc, stock
    global length
    sheets.add_item(length,item)
    length += 1
    await interaction.response.send_message('Item(s) Added to Shop',ephemeral=True)
    # await interaction.channel.send("Item Added to Shop")




@bot.tree.command()
async def shop(interaction):

    mainshop = {}
    count = 0

    items = sheets.get_all_values()
    for item in items:
        item = {'name':item[0], 'price': item[1], 'id':item[3], 'desc':item[2], 'stock':item[4], 'tier':int(item[5])}
        tier = item['tier']
        if tier in mainshop.keys():
            mainshop[tier].append(item)
            count+=1
        else:
            mainshop[tier] = []
            mainshop[tier].append({'name': f'Tier {tier}'})
            mainshop[tier].append(item)
            count +=2

    emlist=[]
    cur_page = 0
    pages = math.ceil(count/10)

    for index in range(pages):
        em=discord.Embed(title='Shop', type='article')
        emlist.append(em)

    index = 0
    for key in mainshop.keys():
        if key != 0:
            for item in mainshop[key]:
                page = math.floor(index/10)
                em = emlist[page]
                index += 1
                name = item['name']
                if name in ['Tier 1', 'Tier 2']:
                    em.add_field(name=name, inline=False, value=' ')
                else:
                    name = item['name']
                    price = item['price']
                    desc = item['desc']
                    stock = item['stock']
                    em.add_field(name=name, value=f" Price: {price} \n Stock: {stock} \n Description: \n{desc}", inline=False)

    # making the embed pages for the shop

    message =  await interaction.channel.send(content=f"Page {cur_page+1}/{pages}:", embed=emlist[0])
    # getting the message object for editing and reacting

    def check(reaction, user):
        return str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")
    #adding reactions to change pages

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
            print("time broken")
        #     break
            # ending the loop if user doesn't react after x seconds



webserver.keep_alive()
bot.run(token)