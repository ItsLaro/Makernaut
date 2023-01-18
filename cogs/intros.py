import discord
import config
from discord.ext import tasks, commands
from datetime import datetime


class Intros(commands.Cog):
    '''
    Commands specifically designed to tackle logistical needs for our Executive Board
    '''

    def __init__(self, bot):
        self.bot = bot
        self.UPE_GUILD_ID = 245393533391863808 if config.isProd else 1065042153836912714
        self.upe_guild = bot.get_guild(self.UPE_GUILD_ID)
        self.MODERATOR_ROLE_ID = 399551100799418370 if config.isProd else 1065046848747872368
        self.INTRO_CHANNEL_ID = 881347138636894218 if config.isProd else 1065042157800542301
        self.intro_channel = self.bot.get_channel(self.INTRO_CHANNEL_ID)
        self.bot_intro_message = None
        
        self.BOT_INTRO_TITLE_TEXT = "Nice to meet you~!"
        self.BOT_INTRO_BODY_TEXT = """ 
My name is **Gui** and I'm the official mascot, friend and virtual assistant of everyone here at **Upsilon Pi Epsilon** at **FIU**.

We want to know more about **YOU**! Post your intro in this channel with the following: 
What's your name? ─ What do you study or work in? Where? ─ What's a fun fact about yourself? ─ Anything else you'd like to share?

*Please **ONLY** post introductions in this channel. If you'd like to start a conversation with someone here, please start a thread or tag them in another relevant channel instead.*
"""
        self.YELLOW_HEX = 0xFFBF00  
        self.bot_intro_embed = discord.Embed(title=self.BOT_INTRO_TITLE_TEXT, description=self.BOT_INTRO_BODY_TEXT, color=self.YELLOW_HEX)
        # self.bot_intro_embed.set_thumbnail(url="https://i.imgur.com/7IyphRI.png")

  
    async def cog_load(self):
        channel = self.intro_channel
        latest_message = None
        async for message in channel.history():
            latest_message = message
            break

        if latest_message and latest_message.author.id == self.bot.user.id:
            self.bot_intro_message = latest_message
        else:
            # We clean channel for stale messages
            async for message in channel.history():
                if message.author.id == self.bot.user.id:
                    await message.delete()
            # Send a new intro message
            self.bot_intro_message = await self.intro_channel.send(embed=self.bot_intro_embed)
            
    @commands.Cog.listener()
    async def on_message(self, payload):
        if payload.channel == self.intro_channel:
            await self.bot_intro_message.delete()
            self.bot_intro_message = await self.intro_channel.send(embed=self.bot_intro_embed)

async def setup(bot):
    await bot.add_cog(Intros(bot)) 