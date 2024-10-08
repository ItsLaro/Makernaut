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
        self.GREEN_HEX = 0x238823 

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
    @app_commands.command(name="purge", description="Mass delete messages")
    @commands.has_permissions(administrator=True)
    async def purge(self, interaction: discord.Interaction, number: int):
        '''
        Deletes multiple messages.
        '''  
        embed_response = discord.Embed(title="<a:verified:798786443903631360> Channel messages purged!", description=f"{number} message{'' if number == 1 else 's deleted'}", color=self.GREEN_HEX)
        await interaction.response.send_message(embed=embed_response, ephemeral=True)
        await interaction.channel.purge(limit=abs(number))

    @app_commands.command(name="help", description="Provides info about different commands")
    async def help_command(self, interaction: discord.Interaction, cog: str = None):
        '''
        Displays this message.
        '''
        try:
            if not cog:
                help = discord.Embed(title='Command Categories',
                                    description='Use `$help Category` to learn more about them!\n(Category Name Must Be in Title Case, Just Like this Sentence.)')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += ('{} - {}'.format(x, self.bot.cogs[x].__doc__) + '\n')
                help.add_field(name='Categories', value=cogs_desc[0:len(cogs_desc)-1], inline=False)
                cmds_desc = ''
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        cmds_desc += ('{} - {}'.format(y.name, y.help) + '\n')
                await interaction.response.send_message(embed=help, ephemeral=True)
            else:
                found = False
                for x in self.bot.cogs:
                    if x.lower() == cog.lower():
                        help = discord.Embed(title=f'{x} Command Listing', description=self.bot.cogs[x].__doc__)
                        for c in self.bot.get_cog(x).get_commands():
                            if not c.hidden:
                                help.add_field(name=c.name, value=c.help, inline=False)
                        found = True
                        break
                if not found:
                    help = discord.Embed(title='Error: No category found!', description=f'What is even a "{cog}"?', color=discord.Color.red())
                await interaction.response.send_message(embed=help, ephemeral=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utilities(bot)) 