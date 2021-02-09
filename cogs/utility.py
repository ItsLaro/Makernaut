import discord
from discord.ext import commands

class Utilities(commands.Cog):

    '''
    Administrative tools to scan integrity of the bot or manage channels
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
    async def ping(self, ctx):
        '''
        Check bot latency.
        '''        
        await ctx.send(f'--Pong! That took {round(self.bot.latency * 1000)}ms')

    # Deletes as many messages as passed in parameter
    @commands.command()
    async def purge(self, ctx, num_messages):
        '''
        Deletes multiple messages.\nThe number corresponds to the number of messages to delete from bottom to top\nEx: $purge 10 
        '''  
        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)

        if mod_role not in roles:
            await ctx.send(
                f'{ctx.author.mention} this command is only meant to be used by Moderators.')
        else:
            await ctx.channel.purge(limit=int(num_messages) + 1)

def setup(bot):
    bot.add_cog(Utilities(bot)) 