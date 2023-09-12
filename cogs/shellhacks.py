import json
import requests
import config
import discord
import traceback
from dotenv import load_dotenv
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

load_dotenv()
SHELLHACKS_API_TOKEN = os.getenv('SHELLHACKS_API_TOKEN')

YELLOW_COLOR = 0xFFBF00  
GREEN_HEX = 0x238823 

SHELLHACKS_ROLE_ID = 1149115195063541840 if config.isProd else 1149115440791027762
SHELLHACKS_DISCORD_SUPPORT_ROLE_ID = 1150551214845603880 if config.isProd else 1150550766927495309
NATIONAL_BOT_LOG_ID = 626541886533795850 if config.isProd else 1065042159679578153

VERIFY_CHANNEL_ID = 1148791017999433788 if config.isProd else 1148818637319319562
BOT_LOG_CHANNEL_ID = 626541886533795850 if config.isProd else 1065042159679578154
ANNOUNCEMENT_CHANNEL_ID = 1148793595780939786 if config.isProd else 1148818637319319562
TEAM_BUILDING_CHANNEL_ID = 1148794152725790820 if config.isProd else 1148818637319319562
WORKSHOPS_CHANNEL_ID = 1149087732862287903 if config.isProd else 1148818637319319562
ACTIVITIES_CHANNEL_ID = 1148794929481523292 if config.isProd else 1148818637319319562
SOCIAL_CHANNEL_ID = 1148799505806925946 if config.isProd else 1148818637319319562
ASK_MLH_CHANNEL_ID = 1148794726514970735 if config.isProd else 1148818637319319562
MENTORSHIP_CHANNEL_ID = 1148792715006459974 if config.isProd else 1148818637319319562
SPONSOR_CHANNEL_ID = 1148792027715223583 if config.isProd else 1148818637319319562

HACKER_GUIDE_SHORTENED_URL = 'https://www.notion.so/weareinit/Hacker-Guide-7deb058ff624449a98391c910f7ad0bd?pvs=4'
VERIFICATION_TOKEN_LENGTH = 4

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
    "Meta": "Meta (formerly Facebook) is a technology giant known for its social media platforms, including Facebook, Instagram, WhatsApp, and a suite of VR technologies (previously Oculus). They connect billions of people globally, shaping the way we communicate and share experiences.",
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

workshop_tracks_info = {
    "Web Development" : "Develop web applications using the latest frameworks and tools",
    "Game Development" : "Create virtual experiences that bring worlds and characters to life", 
    "Hardware" : "Use computer hardware to tackle and solve real-world problems", 
    "Design & Product" : "Create intuitive user experiences for your web or mobile applications", 
    "Mobile Development": "Build interactive mobile applications for iOS and Android platforms",
    "AI & Machine Learning": "Implement AI/ML algorithms to automate tasks and make predictions",
    "IT & Cybersecurity": "Dive into the world of cloud computing, cybersecurity, and hacking",
    "Career Development": "Explore careers in technology and how to break into the industry",
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

def get_response_from_api_send_email(email, discord_id):
    data = {
        "email": email,
        "discord_id": str(discord_id)
    }
    res = requests.post(
        f'https://{"" if config.isProd else "dev."}shellhacks.net/api/admin/sendDiscordEmail', 
        json=data, 
        headers={'Authorization': SHELLHACKS_API_TOKEN, 'Content-Type': 'application/json',}, 
    )
    return res

def get_response_from_api_verify_discord(email, discord_id, discord_username, verification_code ):
    data = {
        "email": email,
        "discord_id": str(discord_id),
        "discord_username": discord_username,
        "verification_code": verification_code 
    }
    print(discord_username)
    res = requests.post(
        f'https://{"" if config.isProd else "dev."}shellhacks.net/api/admin/verifyDiscordAccount', 
        json=data,
        headers={'Authorization': SHELLHACKS_API_TOKEN, 'Content-Type': 'application/json',},
    )
    return res

class ShellHacks(commands.GroupCog, name="shell"):

    '''
    ShellHacks 2023 related functionality.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.verification_channel = self.bot.get_channel(VERIFY_CHANNEL_ID)
        self.announcement_channel = self.bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        self.team_building_channel = self.bot.get_channel(TEAM_BUILDING_CHANNEL_ID)
        self.workshops_channel = self.bot.get_channel(WORKSHOPS_CHANNEL_ID)
        self.activities_channel = self.bot.get_channel(ACTIVITIES_CHANNEL_ID)
        self.social_channel = self.bot.get_channel(SOCIAL_CHANNEL_ID)
        self.ask_mlh_channel = self.bot.get_channel(ASK_MLH_CHANNEL_ID)
        self.mentorship_channel = self.bot.get_channel(MENTORSHIP_CHANNEL_ID)
        self.sponsor_channel = self.bot.get_channel(SPONSOR_CHANNEL_ID)

    async def cog_load(self):
        embed_title = "Link your Discord with ShellHacks 2023!"

        # If message already exists, we leave channel alone
        async for message in self.verification_channel.history():
            if message.author.id == self.bot.user.id and len(message.embeds) > 0 and message.embeds[0].title == embed_title:
                return

        message_1 = f"""
‎ 
Welcome to the **ShellHacks 2023**! 🎉 

Florida's Largest Hackathon welcomes you to its seventh iteration, taking place this weekend (September 15 - 17th) fully person at Florida International University, Biscayne Bay Campus in Miami! ☀️ 

•  💻 Attend technical workshops to learn the latest web, mobile, game dev, AI/ML, hardware, IT/Cybersecurity, and UX/UI technologies!

•  🔨 Build innovative projects with fellow students to gain experience you can add to your resume and make you a stronger candidate!

•  📢 Network with recruiters from top tech companies like Microsoft, Xbox, Google, Waymo, Meta, NVIDIA, Adobe, and more at our sponsor fair and possibly land an internship or job!

•  🚀 Win amazing prizes including MacBooks, iPads, PS5s, and more tech gadgets!

•  🎉 Participate in fun activities such as our Smash Tournament, Women in Tech Meetup, and Cup Stacking!

•  👕 Grab tons of cool swag such as t-shirts, bags, stickers, and more!

•  🥘 Enjoy great food - brunch, lunch, dinner, and snacks are provided the whole weekend!
‎ 
        """

        message_2 = f"""
🏁 **Link My Discord?** 🏁 

Despite being fully in person, Discord remains as one of our main forms of instant communication during the event. Not only that, it's also the perfect place to meet, socialize and coordinate with fellow hackers before and during the event. 
Only hackers that are *Confirmed* or *Checked In* will be able to complete this process and gain access to the entirety of the channels designed for ShellHacks.

In addition to associating your Discord user with your ShellHacks account, the name on the application will be set as your server's nickname. 
This is important to foster a warmer and safer community and will only be visible to others in the server.  

🚀 **Things to Try Here** 🚀 

•  An Annoucement channel ({self.announcement_channel.mention}) will be used to broadcast important information exclusive for those already at ShellHacks.
•  Still don't have a team? Missing one or two members? Head over to the Team Building channel ({self.team_building_channel.mention}), where you can join forces with fellow hacker.
•  On the Ask MLH channel ({self.ask_mlh_channel.mention}) you'll be able to ask hackathon related inquiries to MLH staff and use the Mentorship channel ({self.mentorship_channel.mention}) to open a ticket where a mentor can assit you. 
•  In the Sponsor channel ({self.sponsor_channel.mention}) you'll find a digital space to connect with our sponsors.
•  Some of these channels will only become available closer to the event, including additional ones for workshops, activities and other social spaces.

_Note: This is not a replacement to your physical check in at the venue on Friday._
‎ 
"""
        # Send new verification message otherwise
        embed_description = "Have you confirmed your attendance? Gain access to the rest of the ShellHacks channels by linking your Discord account with your Shellhacks'23 account."
        embed_response = discord.Embed(title=embed_title, description=embed_description, color=discord.Color.blurple())
        embed_response.add_field(name="Not sure what ShellHacks is?", value=f"Learn more at https://www.shellhacks.net/")

        button = InitiateControls()
        with open('assets/SH_Animated_Logo.gif', 'rb') as file:
            gif = discord.File(file)
            await self.verification_channel.send(file=gif)
        await self.verification_channel.send(content=message_1) 
        await self.verification_channel.send(content=message_2, embed=embed_response, view=button) 
   
    #Commands
    @app_commands.command(name="sponsors", description="Creates threads for all sponsors")
    @commands.has_permissions(administrator=True)
    async def sponsor(self, interaction: discord.Interaction):
        '''
        Creates threads for all sponsors
        '''        
        sponsors_forum_channel = self.bot.get_channel(SPONSOR_CHANNEL_ID)

        if config.isProd and len(sponsors_forum_channel.threads) > 0:
            await interaction.response.send_message(f"Couldn't complete action as the channel needs to be empty...", ephemeral=True)
            return
        else:
            await interaction.response.defer()
        
        sponsors_list = list(sponsor_info.keys())
        sponsor_object_list = [HackathonSponsor(sponsor_name, sponsor_info[sponsor_name]) for sponsor_name in sponsors_list]

        for sponsor in reversed(sponsor_object_list):
            if sponsor is not None:
                print(sponsor.name)
                await sponsors_forum_channel.create_thread(name=sponsor.name, content=f'# {sponsor.description}', file=sponsor.image)     
        await interaction.followup.send(f"{len(sponsors_list)} sponsor subthreads created in {sponsors_forum_channel.mention}", ephemeral=True)

    @app_commands.command(name="tracks", description="Creates threads for all workshop tracks")
    @commands.has_permissions(administrator=True)
    async def tracks(self, interaction: discord.Interaction):
        '''
        Creates threads for all sponsors
        '''        
        WORKSHOPS_CHANNEL_ID = 1149087732862287903 if config.isProd else 1148832420506906644
        workshops_forum_channel = self.bot.get_channel(WORKSHOPS_CHANNEL_ID)

        if config.isProd and len(workshops_forum_channel.threads) > 0:
            await interaction.response.send_message(f"Couldn't complete action as the channel needs to be empty...", ephemeral=True)
            return
        else:
            await interaction.response.defer()
        
        workshop_list = list(workshop_tracks_info.keys())
        sponsor_object_list = [HackathonWorkshopTrack(track_name, workshop_tracks_info[track_name]) for track_name in workshop_list]

        for track in reversed(sponsor_object_list):
            if track is not None:
                print(track.name)
                await workshops_forum_channel.create_thread(name=track.name, content=f'# {track.description}', file=track.image)     
        await interaction.followup.send(f"{len(workshop_list)} sponsor subthreads created in {workshops_forum_channel.mention}", ephemeral=True)

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
        if os.path.exists(png_path):
            with open(png_path, "rb") as png_file:
                self.image = discord.File(png_file)

class HackathonWorkshopTrack:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.image = None
        self.load_png()

    def load_png(self):
        png_path = os.path.join(os.path.dirname(__file__), "..", "assets", "SH23_Workshops", f"{self.name}.png")
        if os.path.exists(png_path):
            with open(png_path, "rb") as png_file:
                self.image = discord.File(png_file)

class InitiateControls (View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Start', style=discord.ButtonStyle.primary ,emoji="🐚", custom_id='shellhacks_verification:initiate_button')
    async def initiate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmailSubmitModal()) 

class VerifyControls (View):
    def __init__(self, previously_used_email):
        self.previously_used_email = previously_used_email
        super().__init__(timeout=900) #times-out after 15 minutes

    @discord.ui.button(label='Verify', style=discord.ButtonStyle.secondary, emoji='🔑')
    async def initiate(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = VerificationCodeSubmitModal(self.previously_used_email)
        await interaction.response.send_modal(modal) 
    
    async def on_timeout(self, interaction: discord.Interaction):
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
        self.response_title = "Error..."
        self.response_description = 'An unknown error occured... The developers have been notified.'
        self.response_footer = ''
        super().__init__(timeout=None, custom_id="verification:email_modal")

    async def on_submit(self, interaction: discord.Interaction):
        shellhacks_hacker_role = interaction.guild.get_role(SHELLHACKS_ROLE_ID)
        shellhacks_support_role = interaction.guild.get_role(SHELLHACKS_DISCORD_SUPPORT_ROLE_ID)
        if shellhacks_hacker_role in interaction.user.roles:
            embed_response = discord.Embed(
                title= '<a:utilsuccess:809713352061354016> Already Verified!',
                description='Your ShellHacks accound and Discord account had been previously linked and everything looks fine here on Discord!',
                color=discord.Color.green(),
            )
            embed_response.set_footer(text=f"If you believe this is a mistake, contact someone with the '@Shellhacks - Discord Support' role")
            await interaction.response.send_message(embed=embed_response, ephemeral=True)
            return
        await interaction.response.defer()
        try:
            # Check that the email address is valid.
            validation = validate_email(self.email.value, check_deliverability=True)

            # Take the normalized form of the email address
            validated_email = validation.email            

            # Hit Shell-Discord endpoint #1
            await interaction.followup.send("Taking a look at our database... Hang on a second~! <:ablobsmile:1060827611506417765>", ephemeral=True)
            response = get_response_from_api_send_email(validated_email, interaction.user.id)
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
            if response.status_code == 200:
                if 'discord_id' in data and data['discord_id'] is not None :         
                    title = '<a:utilsuccess:809713352061354016> Already Verified!'
                    description = 'Your ShellHacks accound and Discord account had been previously linked!'
                    color = discord.Color.green()

                    shellhacks_hacker_role = interaction.guild.get_role(SHELLHACKS_ROLE_ID)
                    shellhacks_support_role = interaction.guild.get_role(SHELLHACKS_DISCORD_SUPPORT_ROLE_ID)
                    if shellhacks_hacker_role not in interaction.user.roles:     
                        await interaction.user.add_roles(shellhacks_hacker_role)             
                        description += f" However, seems like you were missing the appropiate role here on Discord. I've gone ahead and attempted to fix that for you! If you still don't get access, please reach out to someone with the {shellhacks_support_role.mention} role"
                    embed_response = discord.Embed(
                        title=title,
                        description=description,
                        color=color,
                    )
                    await interaction.followup.send(embed=embed_response, ephemeral=True)
                    return

                else:
                    embed_response = discord.Embed(
                        title="Check your inbox to verify!", 
                        description="I've sent a code to the email address you provided. Please click below and enter the code in the dialog.", 
                        color=YELLOW_COLOR,
                    )
                    embed_response.set_footer(text="Completing this process will change your server nickname to your real name and unlock the rest of the channels for ShellHacks'23.")
                    button = VerifyControls(validated_email)
                    await interaction.followup.send(embed=embed_response, view=button, ephemeral=True)
                    return
            # ERROR HANDLING
            elif response.status_code == 404:
                self.response_title ="<a:utilfailure:809713365088993291> The email doesn't not seem to be associated with a confirmed ShellHacks application."
                self.response_description ="No match found associated with that email address. Please make sure to use the same email address you used to apply and that you had confirmed your attendance."      
            elif response.status_code == 400:
                if 'application_status' in data and data['application_status'] == "accepted":
                    self.response_title ="<a:utilfailure:809713365088993291> Seems like you haven't confirmed your attendance."
                    self.response_description ="Before linking your accounts, confirm that you will be attending ShellHacks 2023 by visiting https://www.shellhacks.net/dashboard. Please try again after doing so."              
                elif 'discord_id' in data and data['discord_id'] is not None and data['discord_id'] != interaction.user.id:
                    self.response_title ="<a:utilfailure:809713365088993291> Seems like you previously completed this step from a different Discord account."
                    self.response_description =f"Switch to the Discord account you used to complete this step. If you believe this is a mistake, reach out to {shellhacks_support_role.mention}." 
                else:
                    self.response_title ="<a:utilfailure:809713365088993291> Seems like you're still on the waitlist..."
                    self.response_description =f"You can verify your status at https://www.shellhacks.net/dashboard. If you believe this is a mistake, reach out to someone with the {shellhacks_support_role.mention} role."          
                    
            else:
                self.response_title ="<a:utilfailure:809713365088993291> Something unexpected happened..."
                self.response_description =f"Please notify one of our Discord moderators for assistance at {shellhacks_support_role.mention}. "                      
                self.response_footer = "The developers have already been notified of this issue."          

        except EmailNotValidError as e:
            # Email is not valid.
            self.response_title = "<a:utilfailure:809713365088993291> Invalid email address!"
            self.response_description = "Please make sure you spelled it correctly."
        
        else:
            embed_response_for_admin = discord.Embed(title=self.response_title,
                        description=self.response_description,
                        color=discord.Color.red(),
            )
            embed_response_for_admin.set_footer(text=self.response_footer)
            embed_response_for_admin.add_field(name="User Info", value=f'Email: {validated_email}', inline=False)
            embed_response_for_admin.add_field(name="Server Response", value=f'{response.status_code}—{response.reason}: {response.text}', inline=False)
            bot_log_channel = interaction.user.guild.get_channel(BOT_LOG_CHANNEL_ID)
            await bot_log_channel.send(f'{(shellhacks_support_role.mention + ", an") if response.status_code != 404 else "An "} error has been encountered by {interaction.user.mention} in {interaction.channel.mention} during **Step 1**:',embed=embed_response_for_admin)
        embed_response = discord.Embed(title=self.response_title,
            description=self.response_description,
            color=discord.Color.red(),
        )
        embed_response.set_footer(text=self.response_footer)
        await interaction.followup.send(embed=embed_response, ephemeral=True)         
    async def on_error(self, interaction: discord.Interaction, error : Exception):
        shellhacks_support_role = interaction.guild.get_role(SHELLHACKS_DISCORD_SUPPORT_ROLE_ID)
        print(traceback.format_exc())
        bot_log_channel = interaction.user.guild.get_channel(BOT_LOG_CHANNEL_ID)
        color = discord.Color.red()
        embed_response = discord.Embed(title='Error traceback:',
                    description=traceback.format_exc(),
                    color=color,
        )
        embed_response.set_footer(text=self.response_footer)
        await bot_log_channel.send(f"{shellhacks_support_role.mention}, an error was caught: ", embed=embed_response)


class VerificationCodeSubmitModal(Modal, title='Enter Verification Code'):
    token_input = TextInput(
        style=discord.TextStyle.short,
        label="Verification Code",
        required=True,
        placeholder="L4R0",
        min_length=VERIFICATION_TOKEN_LENGTH,
        max_length=VERIFICATION_TOKEN_LENGTH,
    )

    def __init__(self, previously_used_email):
        self.response_title = "Error..."
        self.response_description = 'An unknown error occured... The developers have been notified.'
        self.reponse_footer=''
        self.previously_used_email = previously_used_email
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        shellhacks_hacker_role = interaction.guild.get_role(SHELLHACKS_ROLE_ID)
        shellhacks_support_role = interaction.guild.get_role(SHELLHACKS_DISCORD_SUPPORT_ROLE_ID)
        bot_log_channel = interaction.user.guild.get_channel(BOT_LOG_CHANNEL_ID)
        
        await interaction.response.defer()

        # Sanitize input and compare with server token
        sanitized_token_input = (''.join(ch for ch in self.token_input.value if ch.isalnum()))

        # Hit Shell-Discord endpoint #2
        response = get_response_from_api_verify_discord(self.previously_used_email, interaction.user.id, interaction.user.name, sanitized_token_input)
        if response.status_code == 200:
            try:
                data = response.json()
                await interaction.user.add_roles(shellhacks_hacker_role)
                if data['first_name'] is not None and data['last_name'] is not None:
                    try:
                        await interaction.user.edit(nick=f"{data['first_name']} {data['last_name'].split()}")
                    except discord.DiscordException:
                        self.reponse_footer='There was an error setting your server nickname. We encourage you to try and set it yourself. If you need assistance, reach out to @Shellhacks - Discord Support'
                        embed_admin_response = discord.Embed(
                            title="Couldn't set server nickname",
                            description=f"{interaction.user.display_name} ({interaction.user.mention}) got verified but could not be assigned \"{data['first_name'].split()[0]} {data['last_name'].split()[0]}\" as their nickname",
                            color=discord.Color.red(),
                        )
                        await bot_log_channel.send(f"{shellhacks_support_role.mention}, a discord error was observed: ", embed=embed_admin_response)
            except json.JSONDecodeError as e:
                self.response_title = 'Verification Failed'
                self.response_description = f'There was an error verifying you account due to a technical error.'
                self.reponse_footer = 'The developers have been notified about this.' 
            except discord.DiscordException:
                self.response_title = 'Verification Failed'
                self.response_description = f'There was an error assigning the correct role. Please contact one someone with the {shellhacks_support_role.mention} role.'
                self.reponse_footer = 'The developers have been notified about this.'  
            else:
                # Send success response
                self.response_title = '<a:utilsuccess:809713352061354016> Verified!'
                self.response_description = 'Your ShellHacks account is now linked with Discord'
                embed_response = discord.Embed(title=self.response_title,
                            description=self.response_description,
                            color=discord.Color.green(),
                )
                embed_response.set_footer(text=self.reponse_footer)
                await interaction.followup.send(embed=embed_response, ephemeral=True)
                return
        # ERROR HANDLING
        elif response.status_code == 404:
            self.response_title = 'Something unexpected happened...'
            self.response_description = 'We encountered an error with the email you had provided. Please try again.' 
            self.reponse_footer = "The developers have already been notified of this issue."                     
        elif response.status_code == 400:
            self.response_title = '<a:utilfailure:809713365088993291> Code mismatch...'
            self.response_description = f'Verification code does not match. Please try again by re-clicking on the Verify button. If this seems to be wrong, reach out to {shellhacks_support_role.mention}.' 
            self.reponse_footer = "Tip: Try copy pasting it if you didn\'t"
            embed_response = discord.Embed(
                title=self.response_title,
                description=self.response_description,
                color=discord.Color.red(),
            )
            embed_response.set_footer(text=self.reponse_footer)
            await interaction.followup.send(embed=embed_response, ephemeral=True)
            return
        else:
                self.response_title ="<a:utilfailure:809713365088993291> Something unexpected happened..."
                self.response_description =f"Please notify someone with the {shellhacks_support_role.mention} role for further assistance" 
                self.reponse_footer = "The developers have also already been notified of this issue."                     
        embed_response = discord.Embed(
                    title=self.response_title,
                    description=self.response_description,
                    color=discord.Color.red(),
        )
        embed_response.set_footer(text=self.reponse_footer)
        await interaction.followup.send(embed=embed_response, ephemeral=True)
        embed_response.add_field(name="User Info", value=f'Email: {self.previously_used_email}', inline=False)   
        embed_response.add_field(name="Server Response", value=f'{response.status_code}—{response.reason}: {response.text}', inline=False)
        await bot_log_channel.send(f'{shellhacks_support_role.mention}, error encountered by {interaction.user.mention} in {interaction.channel.mention} during **Step 2**:',embed=embed_response)  
        
    async def on_error(self, interaction: discord.Interaction, error : Exception):
        shellhacks_support_role = interaction.guild.get_role(SHELLHACKS_DISCORD_SUPPORT_ROLE_ID)
        print(traceback.format_exc())
        bot_log_channel = interaction.user.guild.get_channel(BOT_LOG_CHANNEL_ID)
        color = discord.Color.red()
        embed_response = discord.Embed(title='Error traceback:',
                    description=traceback.format_exc(),
                    color=color,
        )
        await bot_log_channel.send(f"{shellhacks_support_role.mention}, an error was caught: ", embed=embed_response)

async def setup(bot):
    await bot.add_cog(ShellHacks(bot)) 