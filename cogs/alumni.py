import config
import discord
from discord.ext import commands
from discord import SelectOption, PartialEmoji
from discord.ui import Select
from helpers.emojis import alphabet

YELLOW_COLOR = 0xFFBF00  
INIT_AA_VERIFIED_ROLE_ID = 1087057030759596122 if config.isProd else 1088343704290480158
RESUME_REVIEWER_ROLE_ID = 1336827376767602759 if config.isProd else 1336829503401496697
RESUME_FORUM_CHANNEL_ID = 1019638833702248469 if config.isProd else 1336830053065035948
DROPDOWN_OPTION_LIMIT = 25
COMPANY_PREFIX = 'Company - '
PROFESSION_PREFIX =  'Professional Role - '
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
            self.add_item(DropdownMenu([entry['option'] for entry in page], [entry['role'] for entry in page], f"Select an Answer [{key}]", f"professional:roles_dropdown_{index}_{key}"))

class Alumni(commands.GroupCog, name="professional"):
    '''
    Provides functionality specific to the INIT Professional chapter category.
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
        body = " ### If you're curently working in the industry and feel comfortable disclosing, please choose your company and professional role from the menu below. "
        footnote = "If your company or role aren't listed, please reach out to a member of the team so we can have it added."
        response_message = f"{title}\n{body}\n{footnote}"

        # If message already exists, we leave channel alone
        async for message in alumni_roles_channel.history():
            if message.author.id == self.bot.user.id:
                return
            else:
                await alumni_roles_channel.purge()
                break

        company_sorted_combined_options_and_roles = await self.fetch_combined_options_and_roles_via_role_prefix(COMPANY_PREFIX)
        company_roles_dropdown_menu_view = SelectView(company_sorted_combined_options_and_roles)

        profession_sorted_combined_options_and_roles = await self.fetch_combined_options_and_roles_via_role_prefix(PROFESSION_PREFIX)
        profession_roles_dropdown_menu_view = SelectView(profession_sorted_combined_options_and_roles)

        image_url = "https://media.discordapp.net/attachments/1112898501714649088/1206182620971405322/Screenshot_18.png?ex=65db141a&is=65c89f1a&hm=375258705e39fe78da47bde19c3d2016eca30af4924980ff5485e0d5490a86b8&=&format=webp&quality=lossless&width=810&height=227"
        await alumni_roles_channel.send(content=image_url) 

        await alumni_roles_channel.send(content=response_message) 

        await alumni_roles_channel.send(content="## Where do you currently work?", view=company_roles_dropdown_menu_view)

        await alumni_roles_channel.send(content="## What's your occupation or position?", view=profession_roles_dropdown_menu_view)

    async def fetch_combined_options_and_roles_via_role_prefix(self, prefix):
        roles = await self.upe_guild.fetch_roles()
        ## Company Roles ##
        company_roles=[]
        prefix_length = len(prefix)
        for role in roles:
            if role.name.startswith(prefix):
                role_name = role.name[prefix_length:]
                emoji_codepoint = alphabet[role_name[0].upper()]
                company_roles.append(role)
        
        sorted_company_roles = sorted(company_roles, key=lambda entry: entry.name.lower())  
        company_options=[]
        for index, role in enumerate(sorted_company_roles):
            role_name = role.name[prefix_length:]
            emoji_codepoint = alphabet[role_name[0].upper()]
            company_options.append(SelectOption(label=role_name, emoji=PartialEmoji(name=emoji_codepoint, animated=False), value=index % DROPDOWN_OPTION_LIMIT))
        company_sorted_combined_options_and_roles = [{'option': option, 'role': role} for option, role in zip(company_options, sorted_company_roles)]
        return company_sorted_combined_options_and_roles

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        """Event listener for when a new thread is created in the resume review forum"""
        if thread.parent_id != RESUME_FORUM_CHANNEL_ID:
            return

        title = "# Welcome to the INIT Resume Review Forum!"
        body = f"""### Hey there {thread.owner.mention}! 

        Resumes are living documents, and can always be fine-tuned. A great resume is the key to getting your foot in the door for life-changing opportunities. 
        
        ### Reminders:
        • Format your title as: `[Target Position] - Your Name`
        • Upload resume as high-quality screenshots (no PDFs or external links)
        • Remove all personal information (phone, address, email)
        
        ### Review Process:
        • Be specific about your target role and industry
        • Mention any specific areas you'd like feedback on
        • Expect feedback within 24-48 hours
        • Ask clarifying questions about the feedback received
        • Consider multiple iterations for best results"""
        footnote = "Remember to maintain a positive attitude and be open to constructive feedback. We're here to help you succeed! 🎯"
        response_message = f"{title}\n{body}\n\n{footnote}"

        embed = discord.Embed(
            description=response_message,
            color=YELLOW_COLOR
        )

        await thread.send(
            content=f"<@&{RESUME_REVIEWER_ROLE_ID}>",
            embed=embed
        )

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
