import importlib
import discord
from discord import app_commands
from discord.ext import commands
import config
import random
import os

MODERATOR_ROLE_ID = 399551100799418370
GREEN_HEX = 0x238823 
HACKER_GUIDE_SHORTENED_URL = 'https://www.notion.so/weareinit/Hacker-Guide-7deb058ff624449a98391c910f7ad0bd?pvs=4'
sponsor_info = {
            "Microsoft": "Microsoft is a multinational technology corporation known for its software products and services.",
            "Vanguard": "Vanguard is an investment management company specializing in mutual funds and ETFs.",
            "Bitstop": "Bitstop is a blockchain technology company providing secure cryptocurrency solutions.",
            "Waymo": "Waymo is a self-driving technology company developing autonomous vehicles.",
            "Mediastream": "Mediastream is a media streaming service offering a wide range of content.",
            "LexisNexis": "LexisNexis is a provider of legal, regulatory, and business information and analytics.",
            "CodePath": "CodePath is an education platform that offers mobile app development courses.",
            "Assurant": "Assurant is a global provider of risk management solutions and insurance services.",
            "Google": "Google is a multinational technology company known for its search engine and online services.",
            "Schonfeld": "Schonfeld is a proprietary trading firm specializing in quantitative and algorithmic trading strategies.",
            "Southwest Airlines": "Southwest Airlines is a major American airline known for its low-cost and customer-friendly approach.",
            "Toren AI": "Toren AI is an artificial intelligence company focused on advancing machine learning technology.",
            "Elfen Software": "Elfen Software is a software development company specializing in innovative solutions.",
            "Addigy": "Addigy is a cloud-based IT management platform for Apple devices.",
            "State Farm": "State Farm is a major insurance and financial services company in the United States.",
            "NVIDIA": "NVIDIA is a leading technology company known for its graphics processing units (GPUs).",
            "Capital One": "Capital One is a diversified bank and financial services company.",
            "Adobe": "Adobe is a multinational software company known for its creative and multimedia software products.",
            "MLT": "MLT (Management Leadership for Tomorrow) is a nonprofit organization dedicated to advancing diversity and leadership.",
            "Miami Dade County": "Miami-Dade County is a county in Florida known for its vibrant community and diverse culture.",
            "Chevron": "Chevron is an American multinational energy corporation involved in the production and exploration of oil and gas.",
            "Wells Fargo": "Wells Fargo is a major American bank and financial services company."
        }

class ShellHacks(commands.GroupCog, name="shell"):

    '''
    Administrative tools to scan integrity of the bot or manage channels
    '''

    def __init__(self, bot):
        self.bot = bot

        
    #Commands
    @app_commands.command(name="sponsors", description="Creates threads for all sponsors")
    @commands.has_permissions(administrator=True)
    async def sponsor(self, interaction: discord.Interaction):
        '''
        Creates threads for all sponsors
        '''        
        SPONSOR_CHANNEL_ID = 1148792027715223583 if config.isProd else 1148832420506906644
        sponsors_forum_channel = self.bot.get_channel(SPONSOR_CHANNEL_ID)
        
        sponsors_list = list(sponsor_info.keys())
        sponsor_object_list = [HackathonSponsor(sponsor_name, sponsor_info[sponsor_name]) for sponsor_name in sponsors_list]

        for sponsor in reversed(sponsor_object_list):
            await sponsors_forum_channel.create_thread(name=sponsor.name, content=sponsor.description, file=sponsor.image)     

    @app_commands.command(name="guide", description="Sends the hacker guide")
    async def guide(self, interaction: discord.Interaction):
        '''
        Sends the hacker guide
        '''
        await interaction.channel.send(generate_hacker_guide_line())

class HackathonSponsor:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.image = None
        self.load_png()
        print(self.image)

    def load_png(self):
        png_path = os.path.join(os.path.dirname(__file__), "..", "assets", "SH23_Sponsors", f"{self.name}.png")
        print(png_path)
        if os.path.exists(png_path):
            with open(png_path, "rb") as png_file:
                self.image = discord.File(png_file)

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

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ShellHacks(bot)) 