import config
import discord
from discord.ext import commands
from discord import SelectOption, PartialEmoji
from discord.ui import Select
from helpers.emojis import alphabet

YELLOW_COLOR = 0xFFBF00  
INIT_AA_VERIFIED_ROLE_ID = 1087057030759596122 if config.isProd else 1088343704290480158
DROPDOWN_OPTION_LIMIT = 2
COMPANY_PREFIX = 'Alumni Company - '
PROFESSION_PREFIX =  'Alumni Role - '
class DropdownMenu (Select):
    def __init__(self, options, roles, placeholder, custom_id):
        self.roles = roles
        super().__init__(options=options, placeholder=placeholder, min_values=1, max_values=1, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        # With the interaction parameter, you can send a response message.
        # With self.values you get a list of the user's selected options.
        selection = int(self.values[0])
        role = self.roles[selection]

        prefix_length = len(COMPANY_PREFIX) if role.name.startswith(COMPANY_PREFIX) else len(PROFESSION_PREFIX)
        role_type = "company" if role.name.startswith(COMPANY_PREFIX) else "occupation"
        role_name = role.name[prefix_length:]

        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"You've selected `{role_name}` as your {role_type}", ephemeral=True)

class SelectView(discord.ui.View):
    def __init__(self, options_and_roles):
        super().__init__(timeout = None)

        options_and_roles_paginated_matrix = split_list(options_and_roles, DROPDOWN_OPTION_LIMIT)
        for index, key in enumerate(options_and_roles_paginated_matrix):
            page = options_and_roles_paginated_matrix[key]
            self.add_item(DropdownMenu([entry['option'] for entry in page], [entry['role'] for entry in page], f"Select an Answer [{key}]", f"alumni:roles_dropdown_{index}"))

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
        title = "# Tell us more about you!"
        body = " # If you're curently working in the industry and feel comfortable disclosing, please choose your company and professional role from the menu below. "
        footnote = "If your company or role aren't listed, please reach out to a member of the team so we can have it added."
        message = f"{title}\n{body}\n{footnote}"

        company_roles_embed_response = discord.Embed(title='Where do you currently work?', description=None, color=YELLOW_COLOR)
        profession_roles_embed_response = discord.Embed(title="What's your occupation or position?", description=None, color=YELLOW_COLOR)

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
        prefix = COMPANY_PREFIX
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
        prefix = PROFESSION_PREFIX
        prefix_length = len(prefix)
        index = 0
        for role in roles:
            if role.name.startswith('Alumni Role'):
                role_name = role.name[prefix_length:]
                emoji_codepoint = alphabet[role_name[0].upper()]
                profession_options.append(SelectOption(label=role_name, emoji=PartialEmoji(name=emoji_codepoint, animated=False), value=index))
                profession_roles.append(role)
                index += 1

        # Combine Option with corresponding Role
        company_combined_options_and_roles = [{'option': option, 'role': role} for option, role in zip(company_options, company_roles)]
        profession_combined_options_and_roles = [{'option': option, 'role': role} for option, role in zip(profession_options, profession_roles)]
        
        # Sort alphabetically
        sorted_company_combined_options_and_roles = sorted(company_combined_options_and_roles, key=lambda entry: entry['role'].name)  
        sorted_profession_combined_options_and_roles = sorted(profession_combined_options_and_roles, key=lambda entry: entry['role'].name)  

        company_roles_dropdown_menu_view = SelectView(sorted_company_combined_options_and_roles)
        profession_roles_dropdown_menu_view = SelectView(sorted_profession_combined_options_and_roles)

        image_url = "https://media.discordapp.net/attachments/825566993754095616/830122620174336011/Artboard_1.png?width=1600&height=450"
        await alumni_roles_channel.send(content=image_url) 
        await alumni_roles_channel.send(content=message) 
        await alumni_roles_channel.send(embed=company_roles_embed_response, view=company_roles_dropdown_menu_view)
        await alumni_roles_channel.send(embed=profession_roles_embed_response, view=profession_roles_dropdown_menu_view)

async def setup(bot):
    await bot.add_cog(Alumni(bot)) 

def split_list(lst, max_elements):
    result = {}
    for i in range(0, len(lst), max_elements):
        sublist = lst[i:i + max_elements]
        first_item_letter = sublist[0]['option'].label[0]
        last_item_letter = sublist[-1]['option'].label[0]
        letter_range =  (first_item_letter + ' - ' + last_item_letter).upper() if first_item_letter != last_item_letter else first_item_letter.upper() 
        key = letter_range if letter_range not in result else letter_range + f'({i})'
        result[key] = sublist
    return result
