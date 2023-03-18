import discord
from discord.ext import commands
from validate_email import validate_email, EmailNotValidError

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
    async def speak_here(self, interaction: discord.Interaction, email: str):
        '''
        Gui will repeat after you.
        '''     
        try:
            # Check that the email address is valid.
            validation = validate_email(email, check_deliverability=True)

            # Take the normalized form of the email address
            # for all logic beyond this point (especially
            # before going to a database query where equality
            # may not take into account Unicode normalization).  
            email = validation.email

            # Use Airtable API in AA member table to locate matching record with email.

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