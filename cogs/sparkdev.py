import discord
from discord.ext import commands

class SparkDev(commands.Cog):

    '''
    Commands specifically designed to tackle logistical needs for UPE SparkDev
    '''
    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(245393533391863808)
        self.MODERATOR_ROLE_ID = 399551100799418370  #Current: Main; Test: 788930867593871381
        self.WHISPERER_ROLE_ID = 797617839355854848 #Additional role for Eboard and Committee members to manage certain commands.

        #Channels
        self.BOT_LOGS_CHANNEL_ID = 626541886533795850
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)
        self.CHECKIN_CHANNEL_ID = 750559851628724275
        self.checkin_channel = self.bot.get_channel(self.CHECKIN_CHANNEL_ID)
        
        #Emails
        self.ai_emails = create_list_from_file("ai.txt")
        self.bsi_emails = create_list_from_file("bsi.txt")
        self.cybersecurity_emails = create_list_from_file("cybersecurity.txt")
        self.dig_emails = create_list_from_file("dig.txt")
        self.embeddedsys_emails = create_list_from_file("embeddedsys.txt")
        self.gamedev_emails = create_list_from_file("gamedev.txt")
        self.iot_emails = create_list_from_file("iot.txt")
        self.it_emails = create_list_from_file("it.txt")
        self.robotics_emails = create_list_from_file("robotics.txt")
        self.vr_emails = create_list_from_file("vr.txt")

    @commands.Cog.listener()
    async def on_message(self, payload):
        if payload.channel == self.checkin_channel:
            if payload.author.id == self.bot.user.id:
                return
            else:
                await payload.delete()

    @commands.command()
    async def teamup(self, ctx, email=None):

        if email == None:
            await ctx.author.create_dm()
            await ctx.author.dm_channel.send('You must input the email you used in your application after the command.\n( Ex: `?teamup email@example.com` ).')
            return
        else:
            lower_email = email.strip().lower()

        if ctx.channel.id == self.CHECKIN_CHANNEL_ID:

            sparkdev_role = discord.utils.get(ctx.guild.roles, id=523307753498738692)
            ai_role = discord.utils.get(ctx.guild.roles, id=746939552999932004)
            bsi_role = discord.utils.get(ctx.guild.roles, id=879094683979092009)
            cybersecurity_role = discord.utils.get(ctx.guild.roles, id=804734475010965534)
            dig_role = discord.utils.get(ctx.guild.roles, id=746944338063392789)
            embeddedsys_role = discord.utils.get(ctx.guild.roles, id=879092820588257311)
            gamedev_role = discord.utils.get(ctx.guild.roles, id=746939550861099079)
            iot_role = discord.utils.get(ctx.guild.roles, id=804724602747879434)
            it_role = discord.utils.get(ctx.guild.roles, id=746944336784261291)
            mobiledev_role = discord.utils.get(ctx.guild.roles, id=746939550592401498)
            robotics_role = discord.utils.get(ctx.guild.roles, id=746944479533072566)
            underline_role = discord.utils.get(ctx.guild.roles, id=746944337308549271)
            vr_role = discord.utils.get(ctx.guild.roles, id=747127660873908354)
            webdev_role = discord.utils.get(ctx.guild.roles, id=746939549644619807)

            roles = [ai_role, bsi_role, cybersecurity_role, dig_role, embeddedsys_role, gamedev_role, iot_role, it_role, mobiledev_role, robotics_role, underline_role, vr_role, webdev_role]

            # check if user has a SparkDev role already
            for role in ctx.author.roles:
                if role in roles:
                    await ctx.author.create_dm()
                    await ctx.author.dm_channel.send('You have already been assigned to a team!\nIf this seems to be a mistake please message someone from the SparkDev Committee.')
                    return

            if lower_email in self.ai_emails:
                team_role = ai_role
            elif lower_email in self.bsi_emails:
                team_role = bsi_role
            elif lower_email in self.cybersecurity_emails:
                team_role = cybersecurity_role
            elif lower_email in self.dig_emails:
                team_role = dig_role
            elif lower_email in self.embeddedsys_emails:
                team_role = embeddedsys_role
            elif lower_email in self.gamedev_emails:
                team_role = gamedev_role
            elif lower_email in self.iot_emails:
                team_role = iot_role
            elif lower_email in self.it_emails:
                team_role = it_role
            elif lower_email in self.robotics_emails:
                team_role = robotics_role
            elif lower_email in self.vr_emails:
                team_role = vr_role
            else:
                await ctx.author.create_dm()
                await ctx.author.dm_channel.send('Email not found...\nPlease make sure you are inputting the email you used in your application. \n( Ex: `?teamup email@example.com` ).')
                return
            await ctx.author.add_roles(team_role)
            await ctx.author.add_roles(sparkdev_role)
            await ctx.author.create_dm()
            await ctx.author.dm_channel.send(f'{ctx.author.mention} you now have **{str(team_role)}** role!')

def create_list_from_file(file_name):
    with open('db/sparkdev/' + file_name) as f:
        return f.read().splitlines()

async def setup(bot):
    await bot.add_cog(SparkDev(bot)) 