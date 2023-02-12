import discord
from discord import app_commands
from discord.ext import commands

class Speak(commands.GroupCog, name="speak"):

    '''
    Administrative tools to scan integrity of the bot or manage channels
    '''

    def __init__(self, bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370
        self.GREEN_HEX = 0x238823 
        self.BLUE_HEX = 0x3895D3
        self.YELLOW_HEX = 0xFFBF00

    #Commands
    @app_commands.command(name="here", description="Gui will repeat after you.")
    @commands.has_permissions(administrator=True)
    async def speak_here(self, interaction: discord.Interaction, message: str):
        '''
        Gui will repeat after you.
        '''     
        await interaction.channel.send(message)
        embed_response = discord.Embed(title="<a:verified:798786443903631360> Message Sent!", description="", color=self.YELLOW_HEX)
        await interaction.response.send_message(embed=embed_response, ephemeral=True)
    
    @app_commands.command(name="somewhere", description="Gui will send a message in speified channel.")
    @commands.has_permissions(administrator=True)
    async def speak_somewhere(self, interaction: discord.Interaction, message: str, channel: discord.TextChannel):
        '''
        Gui will repeat after you.
        '''     
        await channel.send(message)
        embed_response = discord.Embed(title="<a:verified:798786443903631360> Message Sent!", description="", color=self.YELLOW_HEX)
        embed_response.add_field(name="Message:", value=f'"{message}"', inline=False)
        embed_response.add_field(name="channel:", value=channel.mention, inline=True)
        await interaction.response.send_message(embed=embed_response, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Speak(bot)) 