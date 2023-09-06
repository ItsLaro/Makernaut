import config
import discord
import traceback
from discord.ext import commands
from discord import app_commands
from discord.ui import TextInput, View, Modal
from email_validator import validate_email, EmailNotValidError
from helpers.airtable import get_record_by_email, store_token_by_record, verify_discord_user
from helpers.mail.email_sender import send_verification_SMTP_email
import importlib
import config
import random
import os

YELLOW_COLOR = 0xFFBF00  
GREEN_HEX = 0x238823 
SHELLHACKS_ROLE_ID = 1149115195063541840 if config.isProd else 1149115440791027762
NATIONAL_BOT_LOG_ID = 626541886533795850 if config.isProd else 1065042159679578153
HACKER_GUIDE_SHORTENED_URL = 'https://www.notion.so/weareinit/Hacker-Guide-7deb058ff624449a98391c910f7ad0bd?pvs=4'
sponsor_info = {
    "Microsoft": "Microsoft is a multinational technology corporation known for developing, manufacturing, supporting, and selling computer software, consumer electronics, personal computers, and related services. They are most famous for their Windows operating system and Office productivity suite.",
    "Mediastream": "Mediastream is a leading media streaming service that offers a vast catalog of movies, TV shows, and original content to subscribers worldwide. With a user-friendly interface and high-quality streaming, Mediastream has become a go-to platform for entertainment enthusiasts.",
    "Vanguard": "Vanguard is a renowned investment management company with a strong focus on mutual funds, exchange-traded funds (ETFs), and retirement solutions. They are known for their low-cost index funds and commitment to providing investors with reliable financial products.",
    "Bitstop": "Bitstop is an innovative blockchain technology company specializing in secure cryptocurrency solutions. They develop cutting-edge software and services to facilitate safe and efficient cryptocurrency transactions, contributing to the growth of the digital economy.",
    "Waymo": "Waymo, a subsidiary of Alphabet Inc. (Google's parent company), is a pioneer in self-driving technology. They are at the forefront of developing autonomous vehicles and shaping the future of transportation with a focus on safety and innovation.",
    "LexisNexis": "LexisNexis is a global provider of legal, regulatory, and business information, offering advanced analytics and data-driven solutions to legal professionals, businesses, and government agencies. They empower decision-makers with critical insights.",
    "Southwest Airlines": "Southwest Airlines is a major American airline known for its commitment to low fares, excellent customer service, and a vast domestic network. They prioritize affordability and convenience, making air travel accessible to millions.",
    "Schonfeld": "Schonfeld is a leading proprietary trading firm specializing in quantitative and algorithmic trading strategies. They leverage cutting-edge technology to navigate financial markets and optimize trading performance.",
    "Toren AI": "Toren AI is a trailblazing artificial intelligence company dedicated to advancing machine learning technology. Their innovative solutions drive automation, data analysis, and decision-making across various industries.",
    "Elfen Software": "Elfen Software is a dynamic software development company that excels in crafting innovative solutions for businesses. They specialize in creating user-friendly software products that streamline operations and drive growth.",
    "Addigy": "Addigy is a cloud-based IT management platform designed for Apple device management. They provide businesses with powerful tools to monitor, secure, and optimize their Apple device fleets, enhancing productivity and security.",
    "Meta": "Meta (formerly Facebook) is a technology giant known for its social media platforms, including Facebook, Instagram, WhatsApp, and Oculus VR. They connect billions of people globally, shaping the way we communicate and share experiences.",
    "Wells Fargo": "Wells Fargo is a prominent American bank and financial services company that offers a wide range of banking, investment, and mortgage services. They are committed to helping customers succeed financially.",
    "State Farm": "State Farm is a leading insurance and financial services company in the United States. They provide a comprehensive suite of insurance products and financial planning services, helping individuals and families protect their futures.",
    "Capital One": "Capital One is a diversified bank and financial services company known for its credit cards, banking, auto loans, and mortgage products. They leverage technology to create seamless financial experiences for customers.",
    "Assurant": "Assurant is a global provider of risk management solutions and insurance services. They safeguard the things that matter most to people and businesses, offering protection, support, and peace of mind.",
    "Google": "Google is a multinational technology company renowned for its search engine, online advertising, cloud computing, and hardware products. They drive innovation and connect people with information worldwide.",
    "CodePath": "CodePath is an educational platform that offers mobile app development courses and resources to empower students and professionals with in-demand coding skills. They bridge the gap between education and industry needs.",
    "Adobe": "Adobe is a multinational software company known for its creative and multimedia software products, including Photoshop, Illustrator, and Adobe Creative Cloud. They empower creatives and businesses to bring their visions to life.",
    "Nvidia": "NVIDIA is a technology leader known for its graphics processing units (GPUs). They play a crucial role in advancing artificial intelligence, gaming, and scientific computing, delivering breakthrough performance and innovation.",
    "MLT": "MLT (Management Leadership for Tomorrow) is a nonprofit organization dedicated to advancing diversity and leadership in business and technology. They provide mentorship and professional development programs to underrepresented talent.",
    "Miami Dade County": "Miami-Dade County is a vibrant and culturally diverse county in Florida. It is known for its beautiful beaches, dynamic arts scene, and thriving business community, making it a hub of creativity and opportunity.",
    "Chevron": "Chevron is a leading American multinational energy corporation engaged in the exploration, production, and refining of oil and gas. They are committed to powering the world with energy solutions that drive progress and sustainability."
}

def generate_hacker_guide_line():
    # List of hackathon guide responses with a beach, Miami, city, and tech theme
    hackathon_guide_responses = [
        "Ahoy, fellow hacker! 🏖️ Your treasure map to hackathon success lies [here.]({})",
        "Bienvenidos a Miami! 🌴 Your hackathon adventure starts with [our guide.]({})",
        "Ride the digital waves to victory! 🌊 The hackathon guide is [waiting for you.]({})",
        "Ready to code by the beach? 🏄‍♂️ Our guide is your sunscreen. [Don't forget to use it.]({})",
        "Miami vibes and tech thrive! 🌇 Check out the [hackathon guide.]({})",
        "Hack the city of Miami with confidence! 🌆 Your guide is just a [click away.]({})",
        "Make your code sizzle like Miami's sun! ☀️ Dive into [our guide.]({})",
        "Tech meets beach in Miami style! 🏝️ Find your hackathon guide [HERE!]({})",
        "Hola, hacker! 🌅 Your hackathon compass points to the guide right [THERE!]({})",
        "Get ready to hack the day away in Miami style! 🌞 The guide is at [your fingertips.]({})",
        "Code your way through the Magic City! ✨ Find guidance in [our hackathon guide.]({})",
        "Unlock the secrets of the city's tech scene! 🌴 The key is [this guide.]({})",
        "Seize the day, hack the night! 🌃 [The guide]({}) is vast!",
        "Hacking the future, one line at a time! 🌊 Hey, wait, don't forget [the guide.]({})",
        "Miami's tech heartbeat is in our guide! 💓 Take a look [over here.]({})",
        "Ready to code under the Miami moon? 🌙 Your guide is a [click]({}) away.",
        "Ripple waves in the hackathon world! 🌊 Start by following [the guide to success.]({})",
        "The code beach is open for business! 🏖️ Find your [guide to the shore.]({})",
        "💻 Get started with the guide: [_The Guide_.]{}",
        "1...2...3... [DALE!!]({}). <:yeetmrworldwide:465726790984269855>",
    ]

    # Randomly select a response and return the string with the injected URL
    random_response = random.choice(hackathon_guide_responses)
    return random_response.format(HACKER_GUIDE_SHORTENED_URL)

class ShellHacks(commands.GroupCog, name="shell"):

    '''
    ShellHacks 2023 related functionality.
    '''

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        VERIFY_CHANNEL_ID = 1148791017999433788 if config.isProd else 1148818637319319562
        verification_channel = self.bot.get_channel(VERIFY_CHANNEL_ID)

        embed_title = "Check-in for ShellHacks 2023!"

        # If message already exists, we leave channel alone
        async for message in verification_channel.history():
            if message.author.id == self.bot.user.id and len(message.embeds) > 0 and message.embeds[0].title == embed_title:
                return

        message = """
‎ 
Welcome to the **ShellHacks 2023**! 🎉 

At imperdiet dui accumsan sit amet nulla facilisi morbi tempus iaculis urna id volutpat lacus laoreet non curabitur gravida arcu ac tortor dignissim convallis aenean et tortor at risus viverra adipiscing at in tellus integer feugiat scelerisque varius morbi enim nunc faucibus a pellentesque sit amet porttitor eget dolor morbi non arcu risus quis varius quam quisque id diam vel quam! 🤗

🏁 **The Goal** 🏁 

•  Vivamus arcu felis bibendum ut tristique et egestas quis ipsum suspendisse ultrices gravida dictum fusce
•  Pellentesque diam volutpat commodo sed egestas egestas fringilla phasellus faucibus scelerisque eleifend donec pretium vulputate
•  Suspendisse in est ante in nibh mauris cursus mattis molestie a iaculis at erat pellentesque
•  Volutpat consequat mauris nunc congue nisi vitae suscipit tellus mauris a diam maecenas sed enim
•  Pretium nibh ipsum consequat nisl vel pretium lectus quam id leo in vitae turpis massa

🚀 **Things to Try** 🚀 

•  Sapien eget mi
•  Id consectetur purus
•  Diam maecenas sed
•  Dictum sit amet
•  Gravida cum sociis
•  Quam elementum pulvinar etiam non 

‎ 
        """

        # Send new verification message otherwise
        embed_description = "Have you confirmed your attendance? Gain access to the rest of the ShellHacks channels by checking in with your email."
        embed_response = discord.Embed(title=embed_title, description=embed_description, color=discord.Color.blurple())
        embed_response.add_field(name="Not sure what ShellHacks is?", value=f"Learn more at https://www.shellhacks.net/")

        button = InitiateControls()

        await verification_channel.send("https://cdn.discordapp.com/attachments/1148791017999433788/1148817210438058004/Shellhacks_Logo_Outlined.gif")
        await verification_channel.send(content=message, embed=embed_response, view=button) 
   
    #Commands
    @app_commands.command(name="sponsors", description="Creates threads for all sponsors")
    @commands.has_permissions(administrator=True)
    async def sponsor(self, interaction: discord.Interaction):
        '''
        Creates threads for all sponsors
        '''        
        SPONSOR_CHANNEL_ID = 1148792027715223583 if config.isProd else 1148832420506906644
        sponsors_forum_channel = self.bot.get_channel(SPONSOR_CHANNEL_ID)

        if len(sponsors_forum_channel.threads) > 0:
            await interaction.response.send_message(f"Couldn't complete action as the channel needs to be empty...", ephemeral=True)
            return
        else:
            await interaction.response.defer()
        
        sponsors_list = list(sponsor_info.keys())
        sponsor_object_list = [HackathonSponsor(sponsor_name, sponsor_info[sponsor_name]) for sponsor_name in sponsors_list]

        for sponsor in reversed(sponsor_object_list):
            await sponsors_forum_channel.create_thread(name=sponsor.name, content=f'# {sponsor.description}', file=sponsor.image)     
        await interaction.followup.send(f"{len(sponsors_list)} sponsor subthreads created in {sponsors_forum_channel.mention}", ephemeral=True)

    @app_commands.command(name="guide", description="Publicly Sends the hacker guide")
    async def guide(self, interaction: discord.Interaction):
        '''
        Sends the hacker guide
        '''
        await interaction.response.send_message(generate_hacker_guide_line())

class HackathonSponsor:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.image = None
        self.load_png()

    def load_png(self):
        png_path = os.path.join(os.path.dirname(__file__), "..", "assets", "SH23_Sponsors", f"{self.name}.png")
        print(png_path)
        if os.path.exists(png_path):
            with open(png_path, "rb") as png_file:
                self.image = discord.File(png_file)
   
class InitiateControls (View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Check-In', style=discord.ButtonStyle.primary ,emoji="🛫", custom_id='shellhacks_verification:initiate_button')
    async def initiate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmailSubmitModal()) 

class VerifyControls (View):
    def __init__(self):
        super().__init__(timeout=900) #times-out after 15 minutes

    @discord.ui.button(label='Verify', style=discord.ButtonStyle.secondary, emoji='🔑')
    async def initiate(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = VerificationCodeSubmitModal()
        await interaction.response.send_modal(modal) 
    
    async def on_timeout(self, interaction: discord.Interaction):
        ####################################################################################
        # Hit Endpoint to Reset check in flow.                                             # 
        ####################################################################################

        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class EmailSubmitModal(Modal, title='Enter your Email Address'):
    email = TextInput(
        style=discord.TextStyle.short,
        label="Email Address",
        required=True,
        placeholder="gui@fiu.edu",
    )

    def __init__(self):
        super().__init__(timeout=None, custom_id="verification:email_modal")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send("Taking a look at our database... Hang on a second~! <:ablobsmile:1060827611506417765>", ephemeral=True)
        try:
            # Check that the email address is valid.
            validation = validate_email(self.email.value, check_deliverability=True)

            # Take the normalized form of the email address
            validated_email = validation.email

            ####################################################################################
            # Hit Endpoint 1 to check record can be found --- this should return Discord ID if already exists
            ####################################################################################
            print(validated_email)
            if OK1:
                if RECORD_NOT_FOUND:
                    embed_response = discord.Embed(
                        title="<a:utilfailure:809713365088993291> The email doesn't not seem to be associated with a confirmed ShellHacks application.", 
                        description="Not match found associated with that email address. Please make sure to use the same email address you used to apply and that you had confirmed your attendance.", 
                        color=discord.Color.red(),
                    )
                    await interaction.followup.send(embed=embed_response, ephemeral=True)

                elif RECORD_FOUND:         
                    ####################################################################################
                    # If Discord ID already existed, user is only missing their role.
                    ####################################################################################
                    if DISCORD_ID is not None:
                        title = '<a:utilsuccess:809713352061354016> Already Verified!'
                        description = 'Your ShellHacks accound and Discord account had been previously linked!'
                        color = discord.Color.green()

                        shellhacks_hacker_role = interaction.guild.get_role(SHELLHACKS_ROLE_ID)
                        if shellhacks_hacker_role not in interaction.user.roles:     
                            await interaction.user.add_roles(shellhacks_hacker_role)             
                            description += " However, seems like you were missing the appropiate role here on Discord. I've gone ahead and attempted to fix that for you!"
                        embed_response = discord.Embed(
                            title=title,
                            description=description,
                            color=color,
                        )
                        embed_response.set_footer(text="If you still don't get access, please reach out to a mod for assistance.")
                        await interaction.followup.send(embed=embed_response, ephemeral=True)

                    else:
                        ####################################################################################
                        # We need to link these accounts by verifying the email address with a token.
                        # We assume the server already sent the token if it replied with OK
                        ####################################################################################

                        embed_response = discord.Embed(
                            title="Check your inbox to verify!", 
                            description="I've sent a code to the email address you provided. Please click below and enter the code in the dialog", 
                            color=YELLOW_COLOR,
                        )
                        button = VerifyControls()
                        await interaction.followup.send(embed=embed_response, view=button, ephemeral=True)

            else:
                embed_response = discord.Embed(
                    title="<a:utilfailure:809713365088993291> Something unexpected happened...", 
                    description="Please try again. The developers have been notified of this.", 
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed_response, view=button, ephemeral=True)
                
        except EmailNotValidError as e:
            # Email is not valid.
            embed_response = discord.Embed(
                title="<a:utilfailure:809713365088993291> Invalid email address!", 
                description="Please make sure you spelled it correctly.", 
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed_response, ephemeral=True)

class VerificationCodeSubmitModal(Modal, title='Enter Verification Code'):
    token_input = TextInput(
        style=discord.TextStyle.short,
        label="Verification Code",
        required=True,
        placeholder="L4R0",
        min_length=8,
        max_length=10,
    )

    def __init__(self):
        self.response_description = 'An unknown error occured... The developers have been notified.'
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer()

        # Sanitize input and compare with server token
        sanitized_token_input = (''.join(ch for ch in self.token_input.value if ch.isalnum())).upper()

        ####################################################################################
        # Hit endpoint 2 which compares tokens with user input and their Discord ID, if correct server stores Discord ID, and sends back 200
        ####################################################################################
        if 200:
            # Give roles to user
            try:
                init_aa_verified_role = interaction.guild.get_role(INIT_AA_VERIFIED_ROLE_ID)
                await interaction.user.add_roles(init_aa_verified_role)
            except Exception as error:
                description = 'There was an error assigning the correct role. Please contact an organizer.' 

            # Send success response
            title = '<a:utilsuccess:809713352061354016> Verified!'
            self.response_description = 'Your INIT Alumni Chapter is now confirmed on Discord'
            color = discord.Color.green()
            embed_response = discord.Embed(title=title,
                        description=self.response_description,
                        color=color,
            )
            await interaction.followup.send(embed=embed_response, ephemeral=True)
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

async def setup(bot):
    await bot.add_cog(ShellHacks(bot)) 