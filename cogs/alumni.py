import config
import discord
import traceback
from discord.ext import commands
from discord import app_commands, SelectOption, PartialEmoji
from discord.ui import TextInput, View, Button, Modal, Select
from email_validator import validate_email, EmailNotValidError
from helpers.airtable import get_record_by_email, store_token_by_record, verify_discord_user
from helpers.mail.email_sender import send_verification_SMTP_email
from helpers.emojis import alphabet

YELLOW_COLOR = 0xFFBF00  
INIT_AA_VERIFIED_ROLE_ID = 1087057030759596122 if config.isProd else 1088343704290480158
             
class DropdownMenu (Select):
    def __init__(self, options, roles, placeholder, custom_id):
        self.roles = roles
        super().__init__(options=options, placeholder=placeholder, min_values=1, max_values=1, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        # With the interaction parameter, you can send a response message.
        # With self.values you get a list of the user's selected options.
        selection = int(self.values[0])
        role = self.roles[selection]

        company_prefix = 'Alumni Company - '
        profession_prefix =  'Alumni Role - '
        prefix_length = len(company_prefix) if role.name.startswith(company_prefix) else len(profession_prefix)
        role_type = "company" if role.name.startswith(company_prefix) else "occupation"
        role_name = role.name[prefix_length:]

        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"You've selected `{role_name}` as your {role_type}", ephemeral=True)

class SelectView(discord.ui.View):
    def __init__(self, company_options, profession_options, company_roles, profession_roles):
        super().__init__(timeout = None)
        self.add_item(DropdownMenu(company_options, company_roles, "Select your Company", "alumni:company_roles_dropdown"))
        self.add_item(DropdownMenu(profession_options, profession_roles, "Choose your Role", "alumni:profession_roles_dropdown"))

class Alumni(commands.GroupCog, name="alumni"):

    '''
    Provides functionality specific to the INIT Alumni chapter category.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370 
        self.UPE_GUILD_ID = 245393533391863808 if config.isProd else 1065042153836912714
        self.upe_guild = bot.get_guild(self.UPE_GUILD_ID)

    async def cog_load(self):
        ALUMNI_ROLES_CHANNEL_ID = 1112899073507336213 if config.isProd else 1112898501714649088
        alumni_roles_channel = self.bot.get_channel(ALUMNI_ROLES_CHANNEL_ID)

        ## Embed ##
        embed_title = "Tell us more about you!"
        embded_description = "If you're curently working in the industry and feel comfortable disclosing, please choose your company and professional role from the menu below. If your company or role aren't listed, please reach out to a member of the team so we can have it added."

        embed_response = discord.Embed(title=embed_title, description=embded_description)

        # If message already exists, we leave channel alone
        # async for message in alumni_roles_channel.history():
        #     if message.author.id == self.bot.user.id and message.embeds[0].title == embed_title_2:
        #         return
        #     else:
        await alumni_roles_channel.purge()

        # We must traverse all roles in search for the relevant ones
        roles = await self.upe_guild.fetch_roles()

        ## Company Roles ##
        company_options=[]
        company_roles=[]
        prefix = 'Alumni Company - '
        prefix_length = len(prefix)
        index = 0
        for role in roles:
            if role.name.startswith(prefix):
                role_name = role.name[prefix_length:]
                emoji_codepoint = alphabet[role_name[0].upper()]
                company_options.append(SelectOption(label=role_name, emoji=PartialEmoji(name=emoji_codepoint, animated=False), value=index))
                company_roles.append(role)
                index += 1
        ## Profession Roles ##
        profession_options=[]
        profession_roles=[]
        prefix = 'Alumni Role - '
        prefix_length = len(prefix)
        index = 0
        for role in roles:
            if role.name.startswith('Alumni Role'):
                role_name = role.name[prefix_length:]
                emoji_codepoint = alphabet[role_name[0].upper()]
                profession_options.append(SelectOption(label=role_name, emoji=PartialEmoji(name=emoji_codepoint, animated=False), value=index))
                profession_roles.append(role)
                index += 1

        # Send message if there are results
        dropdown_menu_view = SelectView(company_options, profession_options, company_roles, profession_roles)
        image_url = "https://media.discordapp.net/attachments/825566993754095616/830122620174336011/Artboard_1.png?width=1600&height=450"
        await alumni_roles_channel.send(content=image_url) 
        await alumni_roles_channel.send(embed=embed_response, view=dropdown_menu_view) 

async def setup(bot):
    await bot.add_cog(Alumni(bot)) 

    