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
        self.WINIT_CHANNEL_ID = 1168626157911027883 if config.isProd else 1168626341000777739
        self.intro_channel = self.bot.get_channel(self.INTRO_CHANNEL_ID)
        self.winit_channel = self.bot.get_channel(self.WINIT_CHANNEL_ID)
        self.bot_intro_message = None
        self.bot_winit_message = None
        
        self.BOT_INTRO_TITLE_TEXT = "Nice to meet you~!"
        self.BOT_INTRO_BODY_TEXT = """ 
            My name is **Gui** and I'm the official mascot, friend and virtual assistant of everyone here at **INIT**.

            We want to know more about **YOU**! Post your intro in this channel with the following: 
            What's your name? ─ What do you study or work in? Where? ─ What's a fun fact about yourself? ─ Anything else you'd like to share?

            We are happy you're here *in it*!

            *Please **ONLY** post introductions in this channel. If you'd like to start a conversation with someone here, please start a thread or tag them in another relevant channel instead.*
        """
        self.YELLOW_HEX = 0xFFBF00  
        self.bot_intro_embed = discord.Embed(title=self.BOT_INTRO_TITLE_TEXT, description=self.BOT_INTRO_BODY_TEXT, color=self.YELLOW_HEX)
        # self.bot_intro_embed.set_thumbnail(url="https://i.imgur.com/7IyphRI.png")

        self.BOT_WINIT_TITLE_TEXT = "We’re **INIT** to **Win It**~! 💰"
        self.BOT_WINIT_BODY_TEXT = """ 
            We want to celebrate **YOUR** accomplishments! Did you recently get an **internship** offer, land a **full-time** **job**, earn a **scholarship**, **graduate**, or simply accomplish something you’re really proud of? Post a message here and share it with the community!

            We also encourage you to celebrate and support your fellow INIT members by reacting to their messages! If you’d like to congratulate them with a written message, please do it by starting a thread (hover over their message and click “create thread” on the right).
        """
        self.BOT_WINIT_FOOTER = "P.S. Members who share their accomplishments will also have a chance to be featured on our newsletter and social media channels! A great opportunity for you to build your brand and expand your network 😎"
        self.YELLOW_HEX = 0xFFBF00  
        self.bot_winit_embed = discord.Embed(title=self.BOT_WINIT_TITLE_TEXT, description=self.BOT_WINIT_BODY_TEXT, color=self.YELLOW_HEX)
        self.bot_winit_embed.set_footer(text=self.BOT_WINIT_FOOTER)
    
    async def cog_load(self):
       await self.setIntroSticky()
       await self.setWinitSticky()
            
    @commands.Cog.listener()
    async def on_message(self, payload):
        try:
            if self.bot_intro_message is not None and payload.channel == self.intro_channel:
                await self.bot_intro_message.delete()
                self.bot_intro_message = await self.intro_channel.send(embed=self.bot_intro_embed)
            if self.bot_winit_message is not None and payload.channel == self.winit_channel:
                await self.bot_winit_message.delete()
                self.bot_winit_message = await self.winit_channel.send(embed=self.bot_winit_embed)
        except discord.errors.NotFound:
            pass 

    async def setIntroSticky(self):
        latest_message = None
        async for message in self.intro_channel.history():
            latest_message = message
            break

        if latest_message and latest_message.author.id == self.bot.user.id:
            self.bot_intro_message = latest_message
        else:
            # We clean channel for stale messages
            async for message in self.intro_channel.history():
                if message.author.id == self.bot.user.id:
                    await message.delete()
            # Send a new intro message
            self.bot_intro_message = await self.intro_channel.send(embed=self.bot_intro_embed)
    
    async def setWinitSticky(self):
        latest_message = None
        async for message in self.winit_channel.history():
            latest_message = message
            break
        if latest_message and latest_message.author.id == self.bot.user.id:
            self.bot_winit_message = latest_message
        else:
            # We clean channel for stale messages
            async for message in self.winit_channel.history():
                if message.author.id == self.bot.user.id:
                    await message.delete()
            # Send a new intro message
            self.bot_winit_message = await self.winit_channel.send(embed=self.bot_winit_embed)

    
async def setup(bot):
    await bot.add_cog(Intros(bot)) 