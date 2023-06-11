import config
import discord
import traceback
from discord.ext import commands
from discord import app_commands
from discord.ui import TextInput, View, Button, Modal
from email_validator import validate_email, EmailNotValidError
from helpers.airtable import get_record_by_email, store_token_by_record, verify_discord_user
from helpers.mail.email_sender import send_verification_SMTP_email

YELLOW_COLOR = 0xFFBF00  
INIT_AA_VERIFIED_ROLE_ID = 1087057030759596122 if config.isProd else 1088343704290480158
             
class RoleMenu (View):
    def __init__(self):
        self.company_options = []
        self.profession_options = []
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an option",max_values=1,min_values=1,options=self.company_options)
    async def select(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EmailSubmitModal()) 

class Alumni(commands.GroupCog, name="alumni"):

    '''
    Provides functionality specific to the INIT Alumni chapter category.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370  

    async def cog_load(self):
        ALUMNI_VERIFY_CHANNEL_ID = 1087566994682949672 if config.isProd else 1087566806820077659
        alumni_verification_channel = self.bot.get_channel(ALUMNI_VERIFY_CHANNEL_ID)

        embed_title = "Verify your INIT Alumni Chapter Membership!"

        # If message already exists, we leave channel alone
        async for message in alumni_verification_channel.history():
            if message.author.id == self.bot.user.id and message.embeds[0].title == embed_title:
                return

        message = """
‎ 
Welcome to the **INIT Alumni Chapter** side of our Discord! 🎉 

If you're curently working in the industry and feel comfortable disclosing, please choose your company from the menu below. 

If your company isn't listed, please reach out to a member of the team so we can have it added. 
        """

        # Send new verification message otherwise
        embed_description = "Are you a member of the INIT Alumni Chapter? Gain access to the alumni section of the server by getting verified through your email."
        embed_response = discord.Embed(title=embed_title, description=embed_description, color=discord.Color.blurple())
        embed_response.add_field(name="Not a member?", value=f"You can apply at https://airtable.com/shrri7hDqYq9tFyki now!")

        menu = RoleMenu()

        await alumni_verification_channel.send("https://media.discordapp.net/attachments/825566993754095616/830122620174336011/Artboard_1.png?width=1600&height=450")
        await alumni_verification_channel.send(content=message, embed=embed_response, view=menu) 


async def setup(bot):
    await bot.add_cog(Alumni(bot)) 