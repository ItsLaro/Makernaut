import discord
import config
from discord.ext import commands
from discord.ui import View
from discord import app_commands

MDC_CAMPUS_CHANNEL_ID = 1171794121841713152 if config.isProd else 1172995616369021089
MDC_ROLE_ID = 1061212832118608037 if config.isProd else 1065042154369585265
WOLFSON_ROLE_ID = 1173052704898158622 if config.isProd else 1173048170670993438
NORTH_ROLE_ID = 1173052863069573190 if config.isProd else 1173048218746101760
KENDALL_ROLE_ID = 1173052902034636811 if config.isProd else 1173048247217037373
WOLFSON_CAMPUS_NAME = 'MDC Wolfson Campus'
NORTH_CAMPUS_NAME = 'MDC North Campus'
KENDALL_CAMPUS_NAME = 'MDC Kendall Campus'

class CampusRoleSelectControls (View):
    def __init__(self):
        super().__init__(timeout=None)

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
        
class Campus(commands.GroupCog, name="campus"):
    '''
    Commands specifically designed to tackle logistical needs for our Executive Board
    '''
    def __init__(self, bot):
        self.bot = bot    

    async def cog_load(self):
        
        mdc_campus_channel = self.bot.get_channel(MDC_CAMPUS_CHANNEL_ID)

        embed_title = "Select Your MDC Campus"
        embed_description = "Please select one or more campuses that you attend to gain access to the rest of the MDC category. Selecting a campus will notify you of announcements and events taking place at that campus. You can remove a campus by clicking on it again."

        # If message already exists, we leave the channel alone
        async for message in mdc_campus_channel.history():
            if message.author.id == self.bot.user.id and message.embeds[0].title == embed_title:
                return
            
        # Send a new Guild start message otherwise
        embed = discord.Embed(title=embed_title, description=embed_description, color=discord.Colour.blurple())
        controls = CampusRoleSelectControls() ## TODO: CampusRoleSelectControls
        await mdc_campus_channel.send(embed=embed, view=controls)
            
    @app_commands.command(name="remind_mdc",
                        description="Used to inquire about a role.")
    @commands.has_permissions(administrator=True)
    async def remind_MDC(self, interaction: discord.Interaction):
        '''
        Used to send reminder to all inactive MDC students to select a campus
        '''   
        mdc_campus_channel = self.bot.get_channel(MDC_CAMPUS_CHANNEL_ID)

        # embed_title = "IMPORTANT: Select Your MDC Campus on the INIT server"
        # embed_description = "This is a reminder to please select your campus at MDC. You need to select the campus (or campuses) that you attend to gain access to the rest of the MDC category here on Discord. Selecting a campus will notify you of announcements and events taking place at that campus. You can remove a campus by clicking on it again."
        # action_call = f'Please go to {mdc_campus_channel.mention} to make a selection.'
        goodbye_message = f'Thank you! Have and amazing weekend! <:ablobheart:1063101988918804551>'
        # embed = discord.Embed(title=embed_title, description=embed_description, color=discord.Colour.blurple())

        mdc_base_role = interaction.guild.get_role(MDC_ROLE_ID)
        mdc_kendall_role = interaction.guild.get_role(KENDALL_ROLE_ID)
        mdc_north_role = interaction.guild.get_role(NORTH_ROLE_ID)
        mdc_wolfson_role = interaction.guild.get_role(WOLFSON_ROLE_ID)
        campus_roles = [mdc_kendall_role, mdc_north_role, mdc_wolfson_role]

        number_activated_campus_members = 0
        number_undecided_campus_members = 0
        number_undecided_unreachable_campus_members = 0

        list_undecided_reached_campus_members = []
        list_undecided_unreachable_campus_members = []

        await interaction.response.defer()

        for member in interaction.guild.members:
            member_roles = member.roles
            if mdc_base_role in member_roles and any(i in campus_roles for i in member_roles):
                number_activated_campus_members+=1
            elif mdc_base_role in member_roles:
                number_undecided_campus_members+=1
                try:
                    user_inbox = await member.create_dm()
                    # await user_inbox.send(embed=embed)
                    await user_inbox.send(goodbye_message)
                    list_undecided_reached_campus_members.append(member.mention)
                except BaseException:
                    number_undecided_unreachable_campus_members+=1
                    list_undecided_unreachable_campus_members.append(member.mention)
                    pass
        response1 = f'''
No. of MDC students with campus selected: {number_activated_campus_members}
No. of MDC students pending selection: {number_undecided_campus_members}
No. of MDC students pending selection that could not be reached: {number_undecided_unreachable_campus_members}
'''
        response2 = f"List of reached out students: {', '.join(list_undecided_reached_campus_members)[:1800]}"
        response3 = f"List of unreachable students: {', '.join(list_undecided_unreachable_campus_members)[:1800]}"       
        print(response1)
        await interaction.followup.send(response1)
        print(response2)
        await interaction.followup.send(response2)
        print(response3)
        await interaction.followup.send(response3)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Campus(bot))