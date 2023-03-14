import discord
from discord.ext import commands, tasks
import datetime
import pytz
import json

class Analytics(commands.cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity = []
        self.GUILDS_CATEGORY_ID = 1065808460492574730
        self.ANALYTICS_FILE = 'db/analytics/analytics.json'
        self.collect_analytics_loop.start()
        
    def cog_unload(self):
        self.scheduler.shutdown()
    
    async def collect_analytics(self, channel):
        messages = []
        delta = datetime.timedelta(days=1)

        for message in channel.history (limit=None, after=now-delta)
            messages.append(message)
        
        return messages

    @tasks.loop(minutes=1)
    async def collection_analytics_loop(self):
        now = datetime.datetime.now(pytz.timezone('US/Eastern'))
        if now.hour == 3 and now.minute == 0:
            await self.collect_analytics()
        else:
            return


    
    