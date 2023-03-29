import discord
from discord.ext import commands, tasks
import datetime
from datetime import time
import pytz
import requests
import json
import os
from airtable import AirtableInterface

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
TIME_TO_RUN = time(hour=8, tzinfo=pytz.timezone('US/Eastern')) # change to datetime

class Analytics(commands.cog):
    def __init__(self, bot):
        self.airtable = AirtableInterface()
        self.bot = bot 
        self.activity = []
        self.ANALYTICS_FILE = 'db/analytics/analytics.json'
        self.GUILD_ID = 245393533391863808
        self.GUILD = self.bot.get_guild(self.GUILD_ID)
        self.collect_analytics_loop.start()
        self.airtable.test()
    
    def cog_unload(self):
        self.collect_analytics_loop.cancel()

    async def get_guilds_and_parties_channels_ids(self, server):
        '''
        Collects all guild and party channel ids
        '''
        category_names = ['Guilds', 'Parties']
        exclude_channel_name = 'townhall'
        channels = self.get_channels_under_category(server, category_names, exclude_channel_name)
        return channels # returns list of channel objects

    async def collect_activity(self, channel_ids):
        '''
        Collects all messages from the previous 24hrs, returns dictionary
        messages_dict = [{channel_id: [messages objects]}]
        '''

        now = datetime.datetime.utcnow('US/Eastern')
        one_day_ago = now - datetime.datetime.timedelta(days=1)
        all_guild_and_party_channel_history = []
        for channel_id in channel_ids:
            guild_and_party_message_history = {}
            channel = self.bot.get_channel(channel_id) # retrieve channel object
            if channel is None:
                print(f'Channel with ID {channel_id} not found.')
                return

            message_history = []
            for message in channel.history(limit=None, after=one_day_ago):
                if message.created_at >= one_day_ago:
                    message_history.append(message)
                else:
                    break
        
            guild_and_party_message_history[channel_id] = message_history
            all_guild_and_party_channel_history.append(guild_and_party_message_history)
        return all_guild_and_party_channel_history
    
    async def collect_analytics_from_message_history(self, all_guild_and_party_channel_history):
        '''
        Collects analytics from messages
        Will return dictionary with the following format
        {channel_id: [list of unique_user objects]}
        '''

        analytics = {}
        for channel_id, messages in all_guild_and_party_channel_history.items():
            unique_users = set()

            for message in messages:
                unique_users.add(message.author.id)
        
            analytics['channel_id'] = channel_id
            analytics['unique_users'] = list(unique_users)
        
        return analytics

    async def check_status(self):
        '''
        Check the status of guilds and return whether we need to upgrade or down level
        If party meets criteria to be a guild, then change the channel ID
        '''
        pass

    @tasks.loop(minutes=TIME_TO_RUN) # change to datetime
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
        await self.collect_analytics_from_message_history(messages=guild_and_party_message_history)
        await self.check_status()