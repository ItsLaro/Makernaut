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
             
class InitiateControls (View):
    @discord.ui.button(label='Initiate', style=discord.ButtonStyle.primary ,emoji="🏁")
    async def initiate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmailSubmitModal()) 

class EmailSubmitModal(Modal, title='Enter your Email Address'):
    email = TextInput(
        style=discord.TextStyle.short,
        label="Email Address",
        required=True,
        placeholder="gui@fiu.edu",
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Check that the email address is valid.
            validation = validate_email(self.email.value, check_deliverability=True)

            # Take the normalized form of the email address
            validated_email = validation.email

            # Use Airtable API in AA member table to locate matching record with email.
            user_record = get_record_by_email(validated_email)

            print(user_record)

            if user_record is None:
                embed_response = discord.Embed(
                    title="<a:utilfailure:809713365088993291> Could not find Alumni Association", 
                    description="Not match found associated with that email address. Please make sure to use the same email address you used to apply.", 
                    color=discord.Color.red(),
                )
                await interaction.response.send_message(embed=embed_response, ephemeral=True)

            elif user_record['fields']["Discord ID"] != 0:
                title = '<a:utilsuccess:809713352061354016> Already Verified!'
                description = 'Your INIT AA Membership had been previously verified!'
                color = discord.Color.green()

                init_aa_verified_role = interaction.guild.get_role(INIT_AA_VERIFIED_ROLE_ID)
                if init_aa_verified_role not in interaction.user.roles:     
                    await interaction.user.add_roles(init_aa_verified_role)             
                    description += " However, seems like you were missing the appropiate role here on Discord. I've gone ahead and attempted to fix that for you!"
                embed_response = discord.Embed(
                    title=title,
                    description=description,
                    color=color,
                )
                embed_response.set_footer(text="If you still don't get access, please reach out to a mod for assistance.")
                response = await interaction.response.send_message(embed=embed_response, ephemeral=True)
            else:
                # Send email with generated verification_token
                verification_token = send_verification_SMTP_email(validated_email)
                # Store verification_token in new Airtable column for the record.
                succeeded = store_token_by_record(user_record, verification_token)

                if succeeded:
                    embed_response = discord.Embed(
                        title="Check your inbox to verify!", 
                        description="I've sent a code to the email address you provided. Please click below and enter the code in the dialog", 
                        color=YELLOW_COLOR,
                    )
                    button = VerifyControls(user_record, verification_token)
                    await interaction.response.send_message(embed=embed_response, view=button, ephemeral=True)
                else:
                    embed_response = discord.Embed(
                        title="<a:utilfailure:809713365088993291> Something unexpected happened...", 
                        description="Please try again. The developers have been notified of this.", 
                        color=discord.Color.red(),
                    )
                    await interaction.response.send_message(embed=embed_response, view=button, ephemeral=True)
                
        except EmailNotValidError as e:
            # Email is not valid.
            embed_response = discord.Embed(
                title="<a:utilfailure:809713365088993291> Invalid email address!", 
                description="Please make sure you spelled it correctly.", 
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_response, ephemeral=True)

class VerifyControls (View):
    def __init__(self, user_record, verification_token):
        self.verification_token = verification_token
        self.user_record = user_record
        super().__init__(timeout=600) #times-out after 10 minutes

    @discord.ui.button(label='Verify', style=discord.ButtonStyle.secondary, emoji='🔑')
    async def initiate(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = VerificationCodeSubmitModal(self.user_record, self.verification_token)
        await interaction.response.send_modal(modal) 
    
    async def on_timeout(self, interaction: discord.Interaction):
        # after a timeout, clean token from AIRTABLE
        store_token_by_record(self.user_record, '')

        for item in self.children:
            item.disabled = True
        message_embed = 'The operation timed out and the code expired, please restart the process'    
        message_embed.add_field(name="Status:", value=f'{"✅ Approved" if self.isApproved else "❌ Rejected"} by {self.decisionByUser.mention}', inline=False)
        
        await self.message.edit(embed=message_embed, view=self)

class VerificationCodeSubmitModal(Modal, title='Enter Verification Code'):
    token_input = TextInput(
        style=discord.TextStyle.short,
        label="Verification Code",
        required=True,
        placeholder="ABCD1234",
        min_length=8,
        max_length=10,
    )

    def __init__(self, user_record, verification_token):
        self.verification_token = verification_token
        self.user_record = user_record
        self.response_description = 'An unknown error occured... The developers have been notified.'
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):

        # Sanitize input and compare with server token
        sanitized_token_input = (''.join(ch for ch in self.token_input.value if ch.isalnum())).upper()
        if  sanitized_token_input == self.verification_token:
            # Store Discord ID of user and erase server token and 
            succeeded = verify_discord_user(self.user_record, interaction.user)

            if succeeded:
                # Give roles to user
                try:
                    init_aa_verified_role = interaction.guild.get_role(INIT_AA_VERIFIED_ROLE_ID)
                    await interaction.user.add_roles(init_aa_verified_role)
                except Exception as error:
                    description = 'There was an error assigning the correct role. Please contact a mod.' 

            # Send success response
            title = '<a:utilsuccess:809713352061354016> Verified!'
            self.response_description = 'Your INIT AA Membership is now confirmed on Discord'
            color = discord.Color.green()
            embed_response = discord.Embed(title=title,
                        description=self.response_description,
                        color=color,
            )
            response = await interaction.response.send_message(embed=embed_response, ephemeral=True)
        else:
            self.response_description = 'The code did not match. Please try again.' 
            raise Exception()

    async def on_error(self, interaction: discord.Interaction, error : Exception):
        title = 'Verification Failed'
        color = discord.Color.red()
        embed_response = discord.Embed(title=title,
                    description=self.response_description,
                    color=color,
        )
        print(traceback.format_exc())
        response = await interaction.response.send_message(embed=embed_response, ephemeral=True)        

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

        embed_title = "Verify your INIT Alumni Association Membership!"
        embed_description = "Are you a member of the INIT AA? Gain access to the alumni section of the server by getting verified through your email."
        embed_response = discord.Embed(title=embed_title, description=embed_description, color=discord.Color.blurple())
        embed_response.add_field(name="Not a member?", value=f"You can apply at https://airtable.com/shrri7hDqYq9tFyki now!")

        button = InitiateControls(timeout=None)

        self.bot_intro_message = await alumni_verification_channel.send(embed=embed_response, view=button)

    #Commands
    @app_commands.command(name="alumni", description="Verify your membership of the INIT AA (Alumni Association)")
    @commands.has_permissions(administrator=True)
    async def verify_alumni(self, interaction: discord.Interaction, email: str):
        '''
        Gui will repeat after you.
        '''     
        

async def setup(bot):
    await bot.add_cog(Verification(bot)) 