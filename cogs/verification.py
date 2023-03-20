import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import TextInput, View, Button
from email_validator import validate_email, EmailNotValidError
from helpers.airtable import get_all_records, get_record_by_email
from helpers.mail.email_sender import gmail_send_verification_code 

AIRTABLE_UPE_BASE_KEY='appIYzWDeROTPg8Yv'
AIRTABLE_UPE_MEMBERSHIP_TABLE_ID='tbluUiP1zIUtP2uwS'

AIRTABLE_UPE_AA_BASE_KEY='appmBfrXhvebmMnbq'
AIRTABLE_UPE_AA_MEMBERSHIP_TABLE_ID='tblGjYHulggH2gGPJ'

class CodeSubmissionView(View):
    code : str = None

    def __init__(self, timeout=900):
        super().__init__(timeout=timeout)

    @discord.ui.textInput(
        label="Verification Code", 
        style=discord.TextStyle.short, 
        label="Email Verification Code",
        required=True,
        placeholder="ABCD1234",
        min_length=8,
        max_lenght=12,
    )
    async def input_code(self, interaction: discord.Interaction, textInput: discord.ui.TextInput):
        #TODO: Implement

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.primary)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        #TODO: Implement
                            

class Verification(commands.GroupCog, name="verify"):

    '''
    Commands to navigate the UPE Calendar of Events!
    '''

    def __init__(self, bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370  

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
                embed_response = discord.Embed(title="Check your inbox to verify!", description="I've sent a code to the email address you provided. Please enter it below", color=discord.Color.green())
                verification_token = gmail_send_verification_code(email)
                #TODO: Store verification_token in new Airtable column for the record.
                code_submission_view = CodeSubmissionView()
                await interaction.response.send_message(embed=embed_response, view=code_submission_view, ephemeral=True)

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