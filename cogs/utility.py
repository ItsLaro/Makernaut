import discord
from discord import app_commands
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
    @app_commands.command(name="ping", description="Echo a ping into the void (checks the bot latency)")
    async def ping(self, interaction: discord.Interaction):
        '''
        Check bot's latency.
        '''        
        await interaction.response.send_message(f'--Pong! That took {round(self.bot.latency * 1000)}ms')

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
    
    @commands.command()
    async def help(self,ctx,*cog):
        """Displays this message."""

        commands.has_permissions(add_reactions=True,embed_links=True)

        try:
            if not cog:
                help=discord.Embed(title='Command Categories',
                                description='Use `$help Category` to learn more about them!\n(Category Name Must Be in Title Case, Just Like this Sentence.)')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += ('{} - {}'.format(x,self.bot.cogs[x].__doc__)+'\n')
                help.add_field(name='Categories',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
                cmds_desc = ''
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        cmds_desc += ('{} - {}'.format(y.name,y.help)+'\n')
                await ctx.send('',embed=help)
            else:
                if len(cog) > 1:
                    help = discord.Embed(title='Error!',description='That is way too many cogs!',color=discord.Color.red())
                    await ctx.send('',embed=help)
                else:
                    found = False
                    for x in self.bot.cogs:
                        for y in cog:
                            if x == y:
                                help=discord.Embed(title=cog[0]+' Command Listing',description=self.bot.cogs[cog[0]].__doc__)
                                for c in self.bot.get_cog(y).get_commands():
                                    if not c.hidden:
                                        help.add_field(name=c.name,value=c.help,inline=False)
                                found = True
                    if not found:
                        help = discord.Embed(title='Error: No category found!',description='What is even a "'+cog[0]+'"?',color=discord.Color.red())
                    else:
                        pass
                    await ctx.send('',embed=help)
        except:
            pass

    @commands.command()
    async def helpdm(self,ctx,*cog):
        """Displays this message."""

        commands.has_permissions(add_reactions=True,embed_links=True)

        try:
            if not cog:
                help=discord.Embed(title='Command Categories',
                                description='Use `$help Category` to learn more about them!\n(Category Name Must Be in Title Case, Just Like this Sentence.)')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += ('{} - {}'.format(x,self.bot.cogs[x].__doc__)+'\n')
                help.add_field(name='Categories',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
                cmds_desc = ''
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        cmds_desc += ('{} - {}'.format(y.name,y.help)+'\n')
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('',embed=help)
            else:
                if len(cog) > 1:
                    help = discord.Embed(title='Error!',description='That is way too many cogs!',color=discord.Color.red())
                    await ctx.message.author.send('',embed=help)
                else:
                    found = False
                    for x in self.bot.cogs:
                        for y in cog:
                            if x == y:
                                help=discord.Embed(title=cog[0]+' Command Listing',description=self.bot.cogs[cog[0]].__doc__)
                                for c in self.bot.get_cog(y).get_commands():
                                    if not c.hidden:
                                        help.add_field(name=c.name,value=c.help,inline=False)
                                found = True
                    if not found:
                        help = discord.Embed(title='Error: No category found!',description='What is even a "'+cog[0]+'"?',color=discord.Color.red())
                    else:
                        await ctx.message.add_reaction(emoji='✉')
                    await ctx.message.author.send('',embed=help)
        except:
            pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utilities(bot)) 