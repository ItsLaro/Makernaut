import discord
from discord.ext import tasks, commands
from datetime import datetime


class Executive(commands.Cog):
    '''
    Commands specifically designed to tackle logistical needs for our Executive Board
    '''

    def __init__(self, bot):
        self.bot = bot
        self.UPE_GUILD_ID = 245393533391863808
        self.upe_guild = bot.get_guild(self.UPE_GUILD_ID)
        self.MODERATOR_ROLE_ID = 399551100799418370  #Current: Main; Test: 788930867593871381
        self.EBOARD_ROLE_ID = 399558426511802368
        self.eboard_role = self.upe_guild.get_role(self.EBOARD_ROLE_ID)
        self.eboard_member = []
        self.STANDUP_CHANNEL_ID = 930724284886822932
        self.standup_channel = self.bot.get_channel(self.STANDUP_CHANNEL_ID)
        self.BOT_LOGS_CHANNEL_ID = 626541886533795850
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)

        for member in self.standup_channel.members:
            if self.eboard_role in member.roles:
                self.eboard_member.append(member)
        self.standup.start()

    def unload(self):
        self.standup.cancel()

    @tasks.loop(minutes=60.0)
    async def standup(self):
        if datetime.now().hour == 12:
            if datetime.today().weekday() in [0, 2, 4]:
                messages = await self.standup_channel.history(limit=100).flatten()
                good_members = [] 
                late_members = []
                are_all_to_date = True

                for message in messages:
                    if message.created_at.day == datetime.now().day:
                        good_members.append(message.author)
                response = f'Eboard members with **PENDING** standups today:\n'

                for member in self.eboard_member:
                    if member not in good_members:
                        are_all_to_date = False
                        response += member.mention + '\n'
                response += "Please send you updates before the end of the day. If you have nothing to report send a message here saying: `No Updates`\n Thank you! <a:utilsparkle:918949131639197716>"

                if are_all_to_date:
                    response = "Everyone seems to have submitted their bidaily standups today.\nWoohoo~! Great job!"

                await self.standup_channel.send(response)

    @commands.command()
    async def debug_eboard(self, ctx):
        if not self.eboard_member:
            response = "No eboard members found..."
        else:
            response = f'I was able to find {len(self.eboard_member)} eboard members to track for updates!'
        await self.log_channel.send(response)    

def setup(bot):
    bot.add_cog(Executive(bot)) 