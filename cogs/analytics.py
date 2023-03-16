import discord
from discord.ext import commands, tasks
import datetime
from datetime import time
import pytz
import requests
import json

AIRTABLE_API_KEY = 'key'
AIRTABLE_BASE_ID = 'key'
AIRTABLE_TABLE_ID = 'key'
TIME_TO_RUN = time(hour=8, tzinfo=pytz.timezone('US/Eastern'))

class Analytics(commands.cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity = []
        self.ANALYTICS_FILE = 'db/analytics/analytics.json'
        self.collect_analytics_loop.start()

    def get_unique_chapter_channel_ids(chapter):
        '''
        Retrieves unique discord channel id's per chapter
        '''
        endpoint = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
        headers = {
            'Authorization': f'Bearer {AIRTABLE_API_KEY}',
            'Content-Type': 'application/json'
        }
        # subject to change, depends on airtable layout
        params = {
            'filterByFormula': f'Chapter="{chapter}"'
        }
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # subject to change, depends on airtable response
        chapter_channel_ids = [record['fields']['Channel_ids'] for record in data['records']] 
        return chapter_channel_ids
        
    
    def cog_unload(self):
        self.collect_analytics_loop.cancel()
    
    #async def collect_analytics(self, category_id):
    #    '''
    #    Collects analytics from response file, and dumps into analytics.json
    #    '''
    #    messages = []
    #    delta = datetime.timedelta(days=1)

    #    for message in channel.history (limit=None, after=now-delta)
     #       messages.append(message)
        
      #  return messages

    @tasks.loop(minutes=TIME_TO_RUN)
    async def collect_analytics_loop(self):
        '''
        Loops for each chapter in INIT
        '''
        chapters = ['FIU', 'MDC', 'FMU']
        for chapter in chapters:
            chapter_channel_ids = self.get_unique_chapter_channel_ids(chapter) # retrieve ids per chapter
            for channel_id in chapter_channel_ids:
                await self.collect_analytics(channel_id) 
        else:
            return



    
    