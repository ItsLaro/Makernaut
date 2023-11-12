import discord
import config
from discord.ext import commands
from discord.ui import View

MDC_CAMPUS_CHANNEL_ID = 1171794121841713152 if config.isProd else 1172995616369021089
WOLFSON_ROLE_ID = 1173052704898158622 if config.isProd else 1173048170670993438
NORTH_ROLE_ID = 1173052863069573190 if config.isProd else 1173048218746101760
KENDALL_ROLE_ID = 1173052902034636811 if config.isProd else 1173048247217037373
WOLFSON_CAMPUS_NAME = 'MDC Wolfson Campus'
NORTH_CAMPUS_NAME = 'MDC North Campus'
KENDALL_CAMPUS_NAME = 'MDC Kendall Campus'

class CampusRoleSelectControls (View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Wolfson", style=discord.ButtonStyle.primary, custom_id='guilds:campus_wolfson_button')
    async def wolfson(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(WOLFSON_ROLE_ID)
        campus_name = WOLFSON_CAMPUS_NAME

        if(role not in interaction.user.roles):
            await interaction.user.add_roles(role)
            response = f"Selected {campus_name}"
        else:
            await interaction.user.remove_roles(role)
            response = f"Removed {campus_name}"

        await interaction.response.send_message(response, ephemeral=True)
    
    @discord.ui.button(label="North", style=discord.ButtonStyle.primary, custom_id='guilds:campus_north_button')
    async def north(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(NORTH_ROLE_ID)
        campus_name = NORTH_CAMPUS_NAME

        if(role not in interaction.user.roles):
            await interaction.user.add_roles(role)
            response = f"Selected {campus_name}"
        else:
            await interaction.user.remove_roles(role)
            response = f"Removed {campus_name}"
        
        await interaction.response.send_message(response, ephemeral=True)
    @discord.ui.button(label="Kendall", style=discord.ButtonStyle.primary, custom_id='guilds:campus_kendall_button')
    async def kendall(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(KENDALL_ROLE_ID)
        campus_name = KENDALL_CAMPUS_NAME

        if(role not in interaction.user.roles):
            await interaction.user.add_roles(role)
            response = f"Selected {campus_name}"
        else:
            await interaction.user.remove_roles(role)
            response = f"Removed {campus_name}"    
        
        await interaction.response.send_message(response, ephemeral=True)
        
class Campus(commands.Cog):
    '''
    Commands specifically designed to tackle logistical needs for our Executive Board
    '''

    def __init__(self, bot):
        self.bot = bot    
    async def cog_load(self):
        
        mdc_campus_channel = self.bot.get_channel(MDC_CAMPUS_CHANNEL_ID)

        embed_title = "Select Your Campus To Gain Access"
        embed_description = "Select one of the campuses below to gain access to the rest of the MDC category. You will only get notified about events taking place at your campus of choice. You can select more than one campus."

        # If message already exists, we leave the channel alone
        async for message in mdc_campus_channel.history():
            if message.author.id == self.bot.user.id and message.embeds[0].title == embed_title:
                return
            
        # Send a new Guild start message otherwise
        embed = discord.Embed(title=embed_title, description=embed_description, color=discord.Colour.blurple())
        controls = CampusRoleSelectControls() ## TODO: CampusRoleSelectControls
        await mdc_campus_channel.send(embed=embed, view=controls)
            
    @commands.Cog.listener()
    async def on_message(self, payload):
        if payload.author.id == self.bot.user.id:
            return
        if self.bot_intro_message is not None and payload.channel == self.intro_channel:
            await self.bot_intro_message.delete()
            self.bot_intro_message = await self.intro_channel.send(embed=self.bot_intro_embed)
        if self.bot_winit_message is not None and payload.channel == self.winit_channel:
            await self.bot_winit_message.delete()
            self.bot_winit_message = await self.winit_channel.send(embed=self.bot_winit_embed)
    
async def setup(bot):
    await bot.add_cog(Campus(bot)) 