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
        self.ANNOUNCEMENT_CHANNEL_ID = 399553386984243220
        self.announcement_channel = self.bot.get_channel(self.ANNOUNCEMENT_CHANNEL_ID)

        for member in self.standup_channel.members:
            if self.eboard_role in member.roles:
                self.eboard_member.append(member)
        self.standup.start()

    def unload(self):
        self.standup.cancel()

    @tasks.loop(minutes=60.0)
    async def standup(self):
        if datetime.today().weekday() in [2, 4]:

            announcements = await self.announcement_channel.history(limit=10).flatten()
            latestAnnouncementURL = announcements[0].jump_url

            if datetime.now().hour == 11: #6AM EST. Server uses UTC. 
                response = "Good morning <@&399558426511802368>! <a:utilsparkle:918949131639197716>\nQuick reminder that standups are due today. Make sure you answer the following questions in a single message:\n\n"
                response += f"**1. What's the progress on your Click Up tasks? (___No Tasks Assigned___ if none).**\n**2. What have you done since your last update?**\n**3. What are you going to be working on today?**\n**4. Is anything blocking your progress?**\n**5. Have you reacted to the most recent Discord announcement:\n**{latestAnnouncementURL}\n**and engaged with our latest social media posts:**\nhttps://www.instagram.com/upefiu/ **?**\n\n" 
                response += "Thank you! Hope you all have a wonderful day!! <:blobheart:799276766069522432>"
                await self.standup_channel.send(response)

            if datetime.now().hour == 22: #5PM EST. Server uses UTC. 
                messages = await self.standup_channel.history(limit=100).flatten()
                good_members = [] 
                late_members = []
                are_all_to_date = True

                for message in messages:
                    if message.created_at.day == datetime.now().day:
                        good_members.append(message.author)
                response = f':warning: Eboard members with **PENDING** standups today:\n'

                for member in self.eboard_member:
                    if member not in good_members:
                        are_all_to_date = False
                        response += member.mention + '\n'
                response += "Please send your updates before the end of the day. If you have no tasks assigned, send a message here saying: `No Tasks Assigned`\nThank you! <a:utilsparkle:918949131639197716>"

                if are_all_to_date:
                    response = "Everyone seems to have submitted their bidaily standups today.\nWoohoo~! Great job! <a:utilsuccess:809713352061354016>"
            
                await self.standup_channel.send(response)


    @commands.command()
    async def debug_eboard(self, ctx):
        if not self.eboard_member:
            response = "No eboard members found..."
        else:
            response = f'I was able to find {len(self.eboard_member)} eboard members to track for updates!'
        await self.log_channel.send(response)    
    
    @commands.command()
    async def debug_time(self, ctx):
        print(datetime.now())
        
def setup(bot):
    bot.add_cog(Executive(bot)) 