import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from prettytable import PrettyTable
from collections.abc import Sequence
import pprint

# https://developers.google.com/sheets/api/guides/concepts
# https://docs.google.com/spreadsheets/d/1y7MaMeZb-XkrvsGVlCYdAfKKdCRJ50TdyU6Tdry6e-o/edit#gid=0
# https://docs.google.com/spreadsheets/d/19F9BQMQD-EOhl_oupPd8xXM_3ZZmUaQ0a9pwO-sksjg/edit#gid=0
# TODO: Create skeleton directing flow of application by an user wanting to rent, add, delete items.

key_file = 'secret_key.json'
scope =  ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(key_file, scope)
client = gspread.authorize(creds)

class Storage(commands.Cog):

    '''
    Control commands to access and manage the inventory on Gspread DB (Google Sheets).
    '''

    def __init__(self, bot):
        self.bot = bot
        self.inventory_requests = [] #users (IDs) trying to access inventory
        self.manage_requests = [] #user(ID) trying to manage inventory (Will only allow one admin at a time)

    #Events
    @commands.Cog.listener()
    async def on_message(self, message):
        '''
        Allows bot to reply to messages (additional to commands).
        Follow up on Inventory Request.
        '''
        author = message.author
        content = message.content
        channel = message.channel
        #print("Message detected! Properties are: ", author, content, channel)
        #print("Requests at start of detection: ", self.inventory_requests)
        if author.id != self.bot.user.id:
            pass

        ##############################################################################
        #                                                                            #
        #           ========= Follow up to !inventory =========                      #
        #                                                                            #
        ##############################################################################

        request_index = 0        
        for user_with_request in self.inventory_requests: #traversing through list of authors that have made inv. requests
 
            if user_with_request  == author.id: 

                if content == '1':
                    sheet1 = client.open('Inventory').get_worksheet(0)
                    
                    # reads entire spreadsheet as a list of lists
                    equipment = sheet1.get_all_records()
                   
                    parsed_equipment = pretty_format(equipment)
                    await channel.send(f"{author.mention} here's a list of our equipment:\n```{parsed_equipment}```")
                    #print("Requests before popping off: ", self.inventory_requests)
                    self.inventory_requests.pop(request_index)
                elif content == '2':
                    sheet2 = client.open('Inventory').get_worksheet(1)
                    snacks = sheet2.get_all_records()
                    #print(snacks)
                    parsed_snacks = pretty_format(snacks)
                    await channel.send(f"{author.mention} here's a list of our snacks:\n```{parsed_snacks}```")
                    #print("Requests before popping off: ", self.inventory_requests)
                    self.inventory_requests.pop(request_index)
                elif content == 'cancel':
                    emoji = '\N{CROSS MARK}'
                    #print("Requests before popping off: ", self.inventory_requests)
                    self.inventory_requests.pop(request_index)
                    await channel.send(f"**{author.name}**, request cancelled. {emoji}")
                else:
                    emoji = '\N{Black Question Mark Ornament}'
                    await channel.send(f'Invalid inventory selection. {emoji}')                        
                
            request_index += 1
            
    #Commands
    @commands.command()
    async def inventory(self, ctx, arg=0):
        '''
        Calls for an inventory. If no argument is provided, bot will listen for next messages coming from user.
        '''
        # Display only available equipment - Item and Quantity.  
        if arg == 1:
            sheet1 = client.open('Inventory').get_worksheet(0)
         
            # read entire spreadsheet
            equipment = sheet1.get_all_records()
                    
            parsed_equipment = pretty_format(equipment)
            await ctx.send(f"{ctx.author.mention} here's a list of our equipment:\n```{parsed_equipment}```")
        elif arg == 2:
            sheet2 = client.open('Inventory').get_worksheet(1)
            snacks = sheet2.get_all_records() #TODO: FIX format
            #print(snacks)
            parsed_snacks = pretty_format(snacks)
            await ctx.send(f"{ctx.author.mention} here's a list of our snacks:\n```{parsed_snacks}```")
        else:
            await ctx.send(f'Hey {ctx.author.mention}\n```Which inventory would you like to check?\n[1] Equipment\n[2] Snacks\n\nType the corresponding option number or "cancel"```')
            self.inventory_requests.append(ctx.author.id)
    
    @commands.command()
    async def search(self, ctx, arg=0):
        '''
        Allows queries to the db.
        '''
        # Display only available equipment - Item and Quantity.  



# function to format spreadsheets to a readable format
def pretty_format(entries):
    table = PrettyTable() 
    table.field_names = entries[0].keys()

    for entry in entries:
        table.add_row(entry.values())

    return table

# cog setup in bot file
def setup(bot):
    bot.add_cog(Storage(bot))