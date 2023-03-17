import discord
from discord.ext import commands, tasks
import datetime
from datetime import time
import pytz
import requests
import json
import os

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
TIME_TO_RUN = time(hour=8, tzinfo=pytz.timezone('US/Eastern'))

class Analytics(commands.cog):
    def __init__(self, bot):
        self.bot = bot 
        self.activity = []
        self.ANALYTICS_FILE = 'db/analytics/analytics.json'
        self.GUILD_ID = 245393533391863808
        self.GUILD = self.bot.get_guild(self.GUILD_ID)
        self.collect_analytics_loop.start()
    
    def cog_unload(self):
        self.collect_analytics_loop.cancel()
    
    def get_airtable_data(self):
        endpoint = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'
        headers =  {
            'Authorization': f'Bearer {AIRTABLE_API_KEY}',
            'Content-Type': 'application/json'
        }
        url = endpoint
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f'Something went wrong with the Airtable query: {e}')
            
        return

    async def get_guilds_and_parties_channels_ids(self, server):
        '''
        Step 1: Collects all guild and party channel ids
        '''
        category_names = ['Guilds', 'Parties']
        exclude_channel_name = 'townhall'
        channels = self.get_channels_under_category(server, category_names, exclude_channel_name)
        return channels # returns list of channel objects

    async def update_airtable_channels(self, channel_ids):
        '''
        Step 2: Update airtable with new channels
        '''
        pass

    async def collect_activity(self, channel_ids):
        '''
        Step 3: Collects all messages from the previous 24hrs, returns dictionary
        messages_dict = {channel_id: [messages objects]}
        '''
        now = datetime.datetime.utcnow('US/Eastern')
        one_day_ago = now - datetime.datetime.timedelta(days=1)

        guild_and_party_message_history = {}
        for channel_id in channel_ids:
            channel = self.bot.get_channel(channel_id) # retrieve channel object
            if channel is None:
                print(f'Channel with ID {channel_id} not found.')
                return

            message_history = []
            async for message in channel.history(limit=None, after=one_day_ago):
                if message.created_at >= one_day_ago:
                    message_history.append(message)
                else:
                    break
        
            guild_and_party_message_history[channel_id] = message_history
        return guild_and_party_message_history
    
    async def calculate_analytics(self, messages):
        '''
        Step 4: Collects analytics from messages, and dumps into analytics.json
        '''
        pass

    async def check_status(self):
        '''
        Step 5: Check the status of guilds and return whether we need to upgrade or down level
        '''
        pass

    @tasks.loop(minutes=TIME_TO_RUN)
    async def collect_analytics_loop(self):
        '''
        Loops at 3am, conducts all processes
        '''
        # Retrieve new parties
        guild_and_party_ids = self.get_guilds_and_parties_channels_ids(server=self.GUILD_ID)
        # update airtable
        await self.update_airtable_channels(channel_ids=guild_and_party_ids) 
        # Collect Activity
        guild_and_party_message_history = await self.collect_activity(channel_ids=guild_and_party_ids)
        # Calculate Analytics
        await self.calculate_analytics(messages=guild_and_party_message_history)
        await self.check_status()