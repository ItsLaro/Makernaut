from datetime import datetime, timedelta, timezone
from xmlrpc.client import boolean
import discord
from discord.ext import commands
from discord import app_commands
import re
import config

class BotContext(commands.Cog):

    '''
    Behaviour of the bot and its sorroundings, including moderation
    '''
    def __init__(self, bot):
        self.bot = bot
        self.UPE_GUILD_ID = 245393533391863808 if config.isProd else 1065042153836912714
        self.upe_guild = bot.get_guild(self.UPE_GUILD_ID)

        self.MODERATOR_ROLE_ID = 399551100799418370 if config.isProd else 1065042154407338039
        self.BOT_LOGS_CHANNEL_ID = 626541886533795850 if config.isProd else 1065042159679578154
        self.EBOARD_BOTSPAM_CHANNEL_ID = 626183709372186635
        self.GENERAL_BOTSPAM_CHANNEL_ID = 401577290863083531    
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)

        # ROLE IDS
        self.FOUNDING_FATHER = 795860784138813520
        self.NATIONAL_BOARD = 831044126194794526
        self.MASCOT = 1069296675853701283
        self.NATIONAL_EXECUTIVE_DIRECTOR = 1082177728985440297
        self.NATIONA_COMMUNITY_MANAGER = 1128469572958290092
        self.CHAPTER_PRESIDENT = 746916839287947295
        self.CHAPTER_VICE = 746917575417397310
        self.MODERATOR = 399551100799418370 
        self.PRO = 1061382576004157571
        self.FIU = 399558426511802368
        self.MDC_WOLFSON = 1061378521093656577
        self.MDC_NORTH = 1150550918991978616
        self.MDC_KENDALL = 1151700581413564416
        self.UM = 1221999581483634719
        self.FMU = 1061378513501950034

        # TESTING ROLE IDS
        self.TESTING_PRESIDENT = 1065042154407338041
    
        self.PROTECTED_ROLES_IDS = [ 
            self.FOUNDING_FATHER,
            self.NATIONAL_BOARD,
            self.MASCOT,
            self.NATIONAL_EXECUTIVE_DIRECTOR,
            self.NATIONA_COMMUNITY_MANAGER,
            self.CHAPTER_PRESIDENT,
            self.CHAPTER_VICE,
            self.MODERATOR, 
            self.PRO,
            self.FIU,
            self.MDC_WOLFSON,
            self.MDC_NORTH,
            self.MDC_KENDALL,
            self.UM,
            self.FMU,
        ] if config.isProd else [
            self.TESTING_PRESIDENT
        ]

        #Colors HEX
        self.BLUE_HEX = 0x3895D3

        self.PROTECTED_ROLES = []
        for role_id in self.PROTECTED_ROLES_IDS:
            self.PROTECTED_ROLES.append(self.upe_guild.get_role(role_id))

        self.url_pattern = r'''(?xi)
            \b
            (							# Capture 1: entire matched URL
            (?:
                https?:				# URL protocol and colon
                (?:
                /{1,3}						# 1-3 slashes
                |								#   or
                [a-z0-9%]						# Single letter or digit or '%'
                                                # (Trying not to match e.g. "URI::Escape")
                )
                |							#   or
                                            # looks like domain name followed by a slash:
                [a-z0-9.\-]+[.]
                (?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj| Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)
                /
            )
            (?:							# One or more:
                [^\s()<>{}\[\]]+						# Run of non-space, non-()<>{}[]
                |								#   or
                \([^\s()]*?\([^\s()]+\)[^\s()]*?\)  # balanced parens, one level deep: (…(…)…)
                |
                \([^\s]+?\)							# balanced parens, non-recursive: (…)
            )+
            (?:							# End with:
                \([^\s()]*?\([^\s()]+\)[^\s()]*?\)  # balanced parens, one level deep: (…(…)…)
                |
                \([^\s]+?\)							# balanced parens, non-recursive: (…)
                |									#   or
                [^\s`!()\[\]{};:'".,<>?«»“”‘’]		# not a space or one of these punct chars
            )
            |					# OR, the following to match naked domains:
            (?:
                (?<!@)			# not preceded by a @, avoid matching foo@_gmail.com_
                [a-z0-9]+
                (?:[.\-][a-z0-9]+)*
                [.]
                (?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tech|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj| Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)
                \b
                /?
                (?!@)			# not succeeded by a @, avoid matching "foo.na" in "foo.na@example.com"
            )
        )'''
        self.gifs_pattern = r'^https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpg|gif|png)$|\W*(tenor.com)\W*|\W*(gfycat.com)\W*|\W*(imgur.com)\W*|\W*(giphy.com)\W*'
        self.mentions_nitro_pattern = r'\W*(discord)\W*|\W*(nitro)\W*'
        self.real_nitro_pattern = r'\W*\b(discord.com)|\W*\b(discordapp.com)\W*|\W*\b(https:\/\/discord.net)\W*'

    async def member_joined_recently(self, member):
        # Get the current time
        current_dateTime =datetime.now(timezone.utc)

        # Calculate the time 12 hours ago
        twelve_hours_ago = current_dateTime - timedelta(hours=12)
        
        # Check if the member's join time is within the last 12 hours
        if member.joined_at >= twelve_hours_ago:
            return True
        else:
            return False
    
    def member_has_protected_roles(self, member):
        is_protected = False
        for role in member.roles:
            if role in self.PROTECTED_ROLES:
                is_protected = True
            else:
                pass
        return is_protected

    async def is_user_sus(self, member):
        return await self.member_joined_recently(member) and not self.member_has_protected_roles(member)
    
    def mentions_everyone(self, message):
        return any(m in message.content for m in ["@here", "@everyone"])
    
    async def delete_message_and_ban_user(self, message, author):                        
            await message.delete()

            SPAM_REPORT_TITLE = "You have been banned..."
            SPAM_REPORT_DESCRIPTION = f"You have been banned from the INIT server as per my automated malicious content detection."
            EMBED_COLOR = 0xD2222D   
            embed_response = discord.Embed(title=SPAM_REPORT_TITLE, description=SPAM_REPORT_DESCRIPTION, color=EMBED_COLOR)
            embed_response.add_field(name="For the following message:", value=f'"{message.content}"', inline=False)
            embed_response.add_field(name="Now what?", value=f'If you feel this was a mistake or would like to make an appeal please reach out to one of the moderators', inline=False)
            embed_response.set_footer(text='If you fail to get ahold of anyone, please send a DM to "Laro" or reach out by email at ivan@weareinit.org with your information')
            user_inbox = await author.create_dm()
            await user_inbox.send(embed=embed_response)
            
            await author.ban(reason = f"Automated Ban for content: {message.content}")

    async def log_outcome(self, message, author, is_ban):
        SPAM_REPORT_TITLE = "Spam Detected" if is_ban else "Suspicious Message Detected"
        SPAM_REPORT_DESCRIPTION = f"Please review carefully!" if is_ban else "Take action accordingly"
        EMBED_COLOR = 0xD2222D if is_ban else 0xFFBF00   

        embed_response = discord.Embed(title=SPAM_REPORT_TITLE, description=SPAM_REPORT_DESCRIPTION, color=EMBED_COLOR)
        embed_response.add_field(name="Original Message", value=f'{message.content}', inline=False)
        embed_response.add_field(name="Author", value= f"{author.mention}", inline=False)
        embed_response.add_field(name="URL", value=f'{message.jump_url}', inline=False)
        embed_response.add_field(name="Resolution", value= "Message **deleted** and member **banned**!" if is_ban else "Nothing! Please Review", inline=False)  
        await self.log_channel.send(content=f"<@&{self.MODERATOR_ROLE_ID}>", embed=embed_response)

    #Events
    @commands.Cog.listener()
    async def on_message(self, message):
        '''
        Allows bot to parse messages
        '''
        author = message.author
        content = message.content.lower()
        # we do not want the bot to reply to itself
        if author.id == self.bot.user.id:
            return

        matching_url = re.findall(pattern=self.url_pattern, string=content)
        matching_gifs = re.findall(pattern=self.gifs_pattern, string=content)
        matching_mentions_nitro = re.findall(pattern=self.mentions_nitro_pattern, string=content) 
        matching_real_nitro = re.findall(pattern=self.real_nitro_pattern, string=content) 

        is_sus = await self.is_user_sus(author)
        if self.mentions_everyone(message):
                if is_sus: 
                    await self.delete_message_and_ban_user(message, author)
                    await self.log_outcome(message, author, True)
                else: 
                    await self.log_outcome(message, author, False)
        elif matching_url:
            if matching_mentions_nitro:
                if matching_real_nitro:
                    pass # Real Discord link
                elif (matching_gifs):
                    pass # Kinda sus, but just media
                else: 
                    # Most likely a scam
                    if is_sus: 
                        await self.delete_message_and_ban_user(message, author)
                        await self.log_outcome(message, author, True)
                    else:
                        await self.log_outcome(message, author, False)

async def setup(bot):
    await bot.add_cog(BotContext(bot)) 
    