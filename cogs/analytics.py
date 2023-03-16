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
        self.GUILD_ID = 245393533391863808
        self.GUILD = self.bot.get_guild(self.GUILD_ID)
        self.collect_analytics_loop.start()

    #def get_unique_chapter_channel_ids(chapter):
    #    '''
    #    Retrieves unique discord channel id's per chapter
    #    '''
    #    endpoint = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'
    #    headers = {
    #        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    #        'Content-Type': 'application/json'
    #    }
    #    # subject to change, depends on airtable layout
    #    params = {
    #        'filterByFormula': f'Chapter="{chapter}"'
    #    }
    #    response = requests.get(endpoint, headers=headers, params=params)
    #    response.raise_for_status()
    #    data = response.json()
#
    #    # subject to change, depends on airtable response
    #    chapter_channel_ids = [record['fields']['Channel_ids'] for record in data['records']] 
    #    return chapter_channel_ids
        
    
    def cog_unload(self):
        self.collect_analytics_loop.cancel()
    
    async def collect_analytics(self, category_id):
        '''
        Collects analytics from response file, and dumps into analytics.json
        '''
        pass

    async def get_guilds_and_parties_channels_ids(self, server):
        category_names = ['Guilds', 'Parties']
        exclude_channel_name = 'townhall'
        channels = self.get_channels_under_category(server, category_names, exclude_channel_name)
        return channels


    async def collect_activity(self, channel_id):
        '''
        Collects all messages from the previous 24hrs, returns dictionary
        messages_dict = {channel_id: [messages objects]}
        '''
        messages_dict = {}
        now = datetime.datetime.utcnow('US/Eastern')
        one_day_ago = now - datetime.datetime.timedelta(days=1)
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            print(f'Channel with ID {channel_id} not found.')
            return

        messages = []
        async for message in channel.history(limit=None, after=one_day_ago):
            if message.created_at >= one_day_ago:
                messages.append(message)
            else:
                break
        
        messages_dict[channel_id] = messages
        return messages_dict


    @tasks.loop(minutes=TIME_TO_RUN)
    async def collect_analytics_loop(self):
        '''
        Loops for each chapter in INIT
        '''
        chapters = ['FIU', 'MDC', 'FMU']
        for chapter in chapters:
            chapter_channel_ids = self.get_unique_chapter_channel_ids(chapter) # retrieve ids per chapter
            for channel_id in chapter_channel_ids:
                activity = await self.get_activity(channel_id) 
        else:
            return



    
    