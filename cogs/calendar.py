import discord
from discord.ext import commands

class Calendar(commands.Cog):

    '''
    Commands to navigate the UPE Calendar of Events!
    '''

    def __init__(self, bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370

    #Events
    # @commands.Cog.listener()
    # async def function():
    #     pass
        
    #Commands
    @commands.command()
    async def events(self, ctx):
        '''
        Check bot's latency.
        '''        
        await ctx.send(f'Work in progress! Anyhow, that took {round(self.bot.latency * 1000)}ms')

async def setup(bot):
    await bot.add_cog(Calendar(bot)) 