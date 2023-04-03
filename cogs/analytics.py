import discord
from discord.ext import commands, tasks
import datetime
from datetime import time
import os
# from ..db import airtable

class Analytics(commands.Cog):
    '''
    Controls all analytics of guilds and parties
    TODO: 1. Upload all data logs to mongodb
          2. Upload analytics collected to airtable frontend
          3. Complete task loops to have it run at 3am everyday
    '''
    def __init__(self, bot):
        # self.airtable = airtable.AirtableInterface()
        self.AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
        self.AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
        self.AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
        self.bot = bot 
        self.GUILD_ID = 245393533391863808
        self.GUILD = self.bot.get_guild(self.GUILD_ID)
        self.collect_analytics_loop.start()
    
    def cog_unload(self):
        self.collect_analytics_loop.cancel()
    
    def get_channels_under_category(self, server, category_names, exclude_channel_name):
        channels_to_return = []

        for category in server.categories:
            if category.name in category_names:
                for channel in category.channels:
                    if channel.name != exclude_channel_name:
                        channels_to_return.append(channel)
        return channels_to_return

    async def get_guilds_and_parties_channels_ids(self, server):
        '''
        Collects all guild and party channel ids
        '''
        category_names = ['Guilds', 'Parties']
        exclude_channel_name = 'townhall'
        channels = self.get_channels_under_category(server, category_names, exclude_channel_name)
        print(channels)
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
    
    async def get_unique_visiters(self, daily_guilds_activity):
        '''
        Collects daily unique visiters from messages
        Will return dictionary with the following format
        {channel_id: [list of unique_user objects]}
        '''

        unique_users = {}
        for channel_id, messages in daily_guilds_activity.items():
            unique_users = set()

            for message in messages:
                unique_users.add(message.author.id)
        
            unique_users['channel_id'] = channel_id
            unique_users['unique_users'] = list(unique_users)
        
        return unique_users

    async def check_status(self):
        '''
        Check the status of guilds and return whether we need to upgrade or down level
        If party meets criteria to be a guild, then change the channel ID
        '''
        pass


        '''
        TODO: Task loop needs to be redone at the end
        '''
    @tasks.loop(minutes=1) # change to datetime
    async def collect_analytics_loop(self):
        '''
        Loops at 3am, conducts all processes
        '''
        # Retrieve new parties
        guild_and_party_ids = await self.get_guilds_and_parties_channels_ids(server=self.GUILD_ID) 
        # Collect Activity
        guild_and_party_message_history = await self.get_daily_messages(channel_ids=guild_and_party_ids)
        # Calculate Analytics
        await self.get_unique_visiters(daily_guilds_activity=guild_and_party_message_history)
        await self.check_status()

async def setup(bot):
    await bot.add_cog(Analytics(bot)) 