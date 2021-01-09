import discord
from discord.ext import commands

class Utilities(commands.Cog):

    '''
    Administrative tools to scan integrity of the bot or manage channels
    '''

    def __init__(self, bot):
        self.bot = bot

    #Events
    # @commands.Cog.listener()
    # async def function():
    #     pass
        
    #Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'--Pong! That took {round(self.bot.latency * 1000)}ms')

    # Deletes as many messages as passed in parameter
    @commands.command()
    async def purge(self, ctx, num_messages):
        # roles = ctx.author.roles
        # admin = ctx.guild.get_role(admin_id)

        # if admin not in roles:
        #     await ctx.send(
        #         f'{ctx.author.mention} this command is only usable by organizers.')
        # else:
        await ctx.channel.purge(limit=int(num_messages) + 1)
        #@commands.command()
        #async def clear(self, ctx, amount):

def setup(bot):
    bot.add_cog(Utilities(bot)) 