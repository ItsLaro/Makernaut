import config
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import TextInput, View, Button, Modal
from email_validator import validate_email, EmailNotValidError
from helpers.airtable import get_all_records, get_record_by_email
from helpers.mail.email_sender import gmail_send_verification_code 

AIRTABLE_UPE_BASE_KEY='appIYzWDeROTPg8Yv'
AIRTABLE_UPE_MEMBERSHIP_TABLE_ID='tbluUiP1zIUtP2uwS'

AIRTABLE_UPE_AA_BASE_KEY='appmBfrXhvebmMnbq'
AIRTABLE_UPE_AA_MEMBERSHIP_TABLE_ID='tblGjYHulggH2gGPJ'

YELLOW_COLOR = 0xFFBF00  
             
class InitiateControls (View):
    @discord.ui.button(label='Verify', style=discord.ButtonStyle.primary)
    async def initiate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerificationCodeSubmitModal()) 

class VerificationCodeSubmitModal(Modal, title='Verify your Email'):
    name = TextInput(
        style=discord.TextStyle.short,
        label="Verification Code",
        required=True,
        placeholder="ABCD1234",
        min_length=8,
        max_length=10,
    )

    async def on_submit(self, interaction: discord.Interaction):

        # Compare input with server token
        if self.name.value == 'AAAAAAAA':
            # Erase server token
            # Store Discord ID of user
            title = 'Verified!'
            description = 'Your INIT Membership is now confirmed on Discord'
            color = discord.Color.green()
            embed_response = discord.Embed(title=title,
                        description=description,
                        color=discord.Color.green(),
            )
            response = await interaction.response.send_message(embed=embed_response, ephemeral=True)
        else:
            raise Exception('Code does not match...')

    async def on_error(self, interaction: discord.Interaction, error : Exception):
        title = 'Verification Failed'
        description = 'The code did not match. Please try again.'
        color = discord.Color.red()
        embed_response = discord.Embed(title=title,
                    description=description,
                    color=discord.Color.red(),
        )
        # response = await interaction.response.send_message(embed=embed_response, ephemeral=True)        
        return error

class Verification(commands.GroupCog, name="verify"):

    '''
    Commands to navigate the UPE Calendar of Events!
    '''

    def __init__(self, bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370  

    async def cog_load(self):
        ALUMNI_VERIFY_CHANNEL_ID = 1087566994682949672 if config.isProd else 1087566806820077659
        alumni_verification_channel = self.bot.get_channel(ALUMNI_VERIFY_CHANNEL_ID)

        # We clean channel for stale messages and resend a new one
        async for message in alumni_verification_channel.history():
            if message.author.id == self.bot.user.id:
                await message.delete()

        # Send a new Guild start message
        embed_title = "Verify your INIT AA Membership!"
        embed_description = "Blah blah blah"
        embed = discord.Embed(title=embed_title, description=embed_description, color=discord.Colour.blurple())

        controls = InitiateControls(timeout=None)

        self.bot_intro_message = await alumni_verification_channel.send(embed=embed, view=controls)

    #Commands
    @app_commands.command(name="alumni", description="Verify your membership of the INIT AA (Alumni Association)")
    @commands.has_permissions(administrator=True)
    async def verify_alumni(self, interaction: discord.Interaction, email: str):
        '''
        Gui will repeat after you.
        '''     
        try:
            # Check that the email address is valid.
            validation = validate_email(email, check_deliverability=True)

            # Take the normalized form of the email address
            email = validation.email

            # Use Airtable API in AA member table to locate matching record with email.
            records = get_all_records(AIRTABLE_UPE_AA_BASE_KEY, AIRTABLE_UPE_AA_MEMBERSHIP_TABLE_ID)
            user_record = get_record_by_email(records, email)

            if user_record is None:
                embed_response = discord.Embed(title="<a:utilfailure:809713365088993291> Could not find Alumni Association membership associated with that email address", description="Please make sure to use the same email address you used to apply.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed_response, ephemeral=True)
            else:
                #TODO: Verify that this works.
                verification_token = gmail_send_verification_code(email)
                #TODO: Store verification_token in new Airtable column for the record.

                embed_response = discord.Embed(title="Check your inbox to verify!", description="I've sent a code to the email address you provided. Please enter it below", color=discord.Color.green())
                modal = VerificationCodeSubmitModal()
                await interaction.response.send_message(embed=embed_response, view=modal, ephemeral=True)

            # If not found:
                # error out

            # Else:
                # proceed
                # write math.rand code in Airtable column
                # send email with code
                # prompt with dialog so that user enters code
                # if match:
                    # associate email row with discord id
                    # clear code
                    
                # else:
                    # fail 

                # after a timeout, clean code
        except EmailNotValidError as e:
            # Email is not valid.
            # The exception message is human-readable.
            embed_response = discord.Embed(title="<a:utilfailure:809713365088993291> Invalid email address!", description="Please make sure you spelled it correctly.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed_response, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Verification(bot)) 