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

class Analytics(commands.cog):
    '''
    Controls all analytics of guilds and parties

    TODO: 1. Upload all data logs to mongodb
          2. Upload analytics collected to airtable frontend
    '''
    def __init__(self, bot):
        self.airtable = AirtableInterface()
        self.bot = bot 
        self.GUILD_ID = 245393533391863808
        self.GUILD = self.bot.get_guild(self.GUILD_ID)
        self.collect_analytics_loop.start()
    
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

    async def get_daily_messages(self, channel_ids):
        '''
        Collects all messages from the previous 24hrs, returns dictionary
        daily_guilds_activity = [{channel_id: [messages objects]}]
        '''

        now = datetime.datetime.utcnow('US/Eastern')
        one_day_ago = now - datetime.datetime.timedelta(days=1)
        daily_guilds_activity = [] # list of guild/parties message history 
        for channel_id in channel_ids:
            channel_message_history = {} # ex. {channel_id: [message_history]}
            channel = self.bot.get_channel(channel_id) # retrieve channel object
            if channel is None:
                print(f'Channel with ID {channel_id} not found.')
                continue

            message_history = [] # previous 24 hour message history 
            for message in channel.history(limit=None, after=one_day_ago):
                if message.created_at >= one_day_ago:
                    message_history.append(message)
                else:
                    break
                
            # add 24 hour message history to channel
            channel_message_history[channel_id] = message_history
            # add channel history to list of all channels
            daily_guilds_activity.append(channel_message_history)

        # returns list of dictionaries
        return daily_guilds_activity 
    
    async def collect_daily_unique_visiters(self, daily_guilds_activity):
        '''
        Collects daily unique visiters from messages
        Will return dictionary with the following format
        {channel_id: [list of unique_user objects]}
        '''

        daily_unique_users = {}
        for channel_id, messages in daily_guilds_activity.items():
            unique_users = set()

            for message in messages:
                unique_users.add(message.author.id)
        
            daily_unique_users['channel_id'] = channel_id
            daily_unique_users['unique_users'] = list(unique_users)
        
        return daily_unique_users

    async def check_status(self):
        '''
        Check the status of guilds and return whether we need to upgrade or down level
        If party meets criteria to be a guild, then change the channel ID
        '''
        pass


        '''
        TODO: Task loop needs to be redone at the end
        '''
    #@tasks.loop(minutes=TIME_TO_RUN) # change to datetime
    #async def collect_analytics_loop(self):
    #    '''
    #    Loops at 3am, conducts all processes
    #    '''
    #    # Retrieve new parties
    #    guild_and_party_ids = self.get_guilds_and_parties_channels_ids(server=self.GUILD_ID) 
    #    # Collect Activity
    #    guild_and_party_message_history = await self.collect_activity(channel_ids=guild_and_party_ids)
    #    # Calculate Analytics
    #    await self.collect_daily_unique_visiters(messages=guild_and_party_message_history)
    #    await self.check_status()