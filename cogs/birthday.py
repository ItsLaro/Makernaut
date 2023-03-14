import discord
from discord import app_commands
from discord.ext import tasks, commands
import config
import asyncio
import datetime
from datetime import date
import os
import pytz
import requests

AIRTABLE_API_KEY = os.environ['UPE_AIRTABLE_API_KEY']
AIRTABLE_BASE_ID = os.environ['UPE_AIRTABLE_BASE_KEY']        
AIRTABLE_TABLE_ID = os.environ['UPE_AIRTABLE_TABLE_ID']
BIRTHDAY_FIELD_ID = 'fldoUSAvFtdsI51FP'
DISCORD_NAME_FIELD_ID = 'fldoUSAvFtdsI51FP'
NAME_FIELD_ID = 'fld3mtI8hayU9UPHD'
YELLOW_COLOR = 0xFFBF00  
RED_COLOR = 0xD2222D

BOT_KEY = os.environ['BOT_KEY']

class Birthday(commands.Cog):
    '''
    Checks 8am every day for birthdays
    If there are birthdays @marketing
    '''

    def __init__(self, bot):
        self.bot = bot
        self.MEMBERSHIP_CHANNEL_ID = 1061194622472298559 if config.isProd else 1065042160426176632 
        self.BOT_LOG_CHANNEL_ID = 626541886533795850 if config.isProd else 1065042159679578154
        self.SPOTLIGHT_CHANNEL_ID = 1019725350701379685
        self.GUILD = bot.get_guild(245393533391863808)
        self.check_birthday.start()
    
    def unload(self):
        self.check_birthday.cancel()

    def get_airtable_data(self):
        '''
        Returns full response json, including pages
        '''

        all_records = []
        endpoint = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
        headers = {
            'Authorization': f'Bearer {AIRTABLE_API_KEY}', 
            'Content-Type': 'application/json'
        }
        url = endpoint
        while True:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                records = data['records']
                all_records.extend(records)
                if 'offset' in data:
                    url = endpoint + '?offset=' + data['offset']
                else:
                    break
            except Exception as e:
                print(f'Something went wrong with the airtable query: {e}')
        
        return all_records


    @tasks.loop(minutes=1)
    async def check_birthday(self):
        '''
        Checks json for birthday, if match, send message with discord names
        '''
        now = datetime.datetime.now()
        current_date = now.strftime("%m-%d")
        date_formatted = now.strftime('%B %d') + ('st' if now.day in [1, 21, 31] else 'nd' if now.day in [2, 22] else 'rd' if now.day in [3, 23] else 'th')
        
        if now.hour == 8 and now.minute == 0:
            records = self.get_airtable_data()
        else:
            return

        if records is not None:
            channel = self.bot.get_channel(self.MEMBERSHIP_CHANNEL_ID)
            response_title = f"<a:blobcake:1063101478321000558> Today's Birthdays: {date_formatted}"
            response_description = "List of INIT Members that are celebrating their birthday's today:"
            embed_color = YELLOW_COLOR
            embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
            birthday_count = 0

            for record in records:
                if 'Birthday' not in record['fields'] or 'Discord User Name' not in record['fields']:
                    continue
                    
                birthday = record['fields']['Birthday']
                if birthday[5:10] == current_date:
                    discord_user_name = record['fields']['Discord User Name']
                    discord_user = discord.utils.get(self.bot.guilds, name=discord_user_name)
                    first_name = record['fields']['First Name']
                    last_name = record['fields']['Last Name']
                    field_name = f"{first_name} {last_name} ({discord_user.mention if discord_user is not None else discord_user_name})"
                    embed_response.add_field(name=field_name, value="\u200b", inline=False)  # '\u200b' is a zero-width space to set an empty value
                    birthday_count += 1
                    
            embed_response.set_footer(text=f'\n\nWrite them something special in the Spotlight channel')
            
        else:
            channel = self.bot.get_channel(self.BOT_CHANNEL_ID)
            response_title = f"<a:utilfailure:809713365088993291> Failed to load birthdays"
            response_description = "Failed to load membership records"
            embed_color = RED_COLOR
            embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
        
        if birthday_count == 0:
            response_title = f"<a:blobcake:1063101478321000558> Today's Birthdays: {date_formatted}"
            response_description = "None of our members are celebrating their birthdays today."
            embed_color = YELLOW_COLOR
            embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
            await channel.send(embed=embed_response)

        await channel.send(embed=embed_response)



async def setup(bot):
    await bot.add_cog(Birthday(bot)) 



