import discord
import config
from discord import app_commands
from discord.ext import tasks, commands
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

BOT_KEY = os.environ['BOT_KEY']

class Birthday(commands.Cog):
    '''
    Checks 8am every day for birthdays
    If there are birthdays @marketing
    '''

    def __init__(self, bot):
        self.bot = bot
        self.MARKETING_CHANNEL_ID = 1065042161265021014 # change in prod
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


    @tasks.loop(minutes=60)
    async def check_birthday(self):
        '''
        Checks json for birthday, if match, send message with discord names
        '''
        now = datetime.datetime.now()
        current_date = now.strftime("%m-%d")
        records = self.get_airtable_data()
        channel = self.bot.get_channel(self.MARKETING_CHANNEL_ID)
        if records is not None:
            # send message to channel
            message = "Good morning <@&1065042154369585270>! <a:sunrise:1084911488151597116> \n\nThese are the members celebrating birthday's today: "
            for record in records:
                if 'Birthday' not in record['fields']:
                    continue
                
                birthday = record['fields']['Birthday']
                if birthday[5:10] == current_date:
                    discord_user_name = record['fields']['Discord User Name']
                    first_name = record['fields']['First Name']
                    last_name = record['fields']['Last Name']
                    message += f' {first_name} {last_name} ({discord_user_name})'
            
            message += '\n\nWrite them something special! <:partying_face:1084911656775200899>'
            await channel.send(message)
        else:
            return


async def setup(bot):
    await bot.add_cog(Birthday(bot)) 



