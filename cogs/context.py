from xmlrpc.client import boolean
import discord
from discord.ext import commands
import re

class BotContext(commands.Cog):

    '''
    Behaviour of the bot and its sorroundings, including moderation
    '''
    def __init__(self, bot):
        self.bot = bot
        self.UPE_GUILD_ID = 245393533391863808
        self.upe_guild = bot.get_guild(self.UPE_GUILD_ID)

        self.MODERATOR_ROLE_ID = 399551100799418370
        self.BOT_LOGS_CHANNEL_ID = 626541886533795850
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)
        self.MODERATOR_ROLE_ID = 399551100799418370  #Current: Main; Test: 788930867593871381

        self.EVERYONE_ROLE_ID = 245393533391863808
        self.CODE_INTEREST_ROLE_ID = 798068011667161128
        self.MAKE_INTEREST_ROLE_ID = 798068011667161128
        self.INFOTECH_INTEREST_ROLE_ID = 798068011667161128
        self.DESIGN_INTEREST_ROLE_ID = 798068011667161128
        self.LEAP_INTEREST_ROLE_ID = 798068011667161128
        self.IGNITE_INTEREST_ROLE_ID = 798068011667161128
        self.SPARKDEV_INTEREST_ROLE_ID = 798068011667161128
        self.SHELLHACKS_INTEREST_ROLE_ID = 798068011667161128
        self.DISCOVER_INTEREST_ROLE_ID = 798068011667161128

        self.ALUMNI_ROLE_ID = 523310392030658573
        self.PAST_SPARKDEV_ROLE_ID = 797573229493354616
        self.SHELLHACKS_2022_ROLE_ID = 933128149938626661
        self.SHELLHACKS_2021_ROLE_ID = 888957354417192960
        self.SHELLHACKS_2020_ROLE_ID = 523306020538286080
    
        self.UNPROTECTED_ROLES_IDS = [ 
            self.EVERYONE_ROLE_ID,
            self.CODE_INTEREST_ROLE_ID, 
            self.MAKE_INTEREST_ROLE_ID, 
            self.INFOTECH_INTEREST_ROLE_ID, 
            self.DESIGN_INTEREST_ROLE_ID, 
            self.LEAP_INTEREST_ROLE_ID, 
            self.IGNITE_INTEREST_ROLE_ID, 
            self.SPARKDEV_INTEREST_ROLE_ID, 
            self.SHELLHACKS_INTEREST_ROLE_ID, 
            self.DISCOVER_INTEREST_ROLE_ID,
            self.ALUMNI_ROLE_ID, 
            self.PAST_SPARKDEV_ROLE_ID,
            self.SHELLHACKS_2022_ROLE_ID,
            self.SHELLHACKS_2021_ROLE_ID,
            self.SHELLHACKS_2020_ROLE_ID,
        ]

        self.UNPROTECTED_ROLES = []
        for role_id in self.UNPROTECTED_ROLES_IDS:
            self.UNPROTECTED_ROLES.append(self.upe_guild.get_role(role_id))

    #Commands
    @commands.command()
    async def speak(self, ctx, *args):
        '''
        Gui will repeat after you.Ex: ?speak Hello World!\nYou can also specify the channel after a `|`.\nEx: ?speak Hello users in another channel! | 808635094373761064
        '''     
        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)

        if (mod_role not in roles):
            return
        if len(args) != 0:
            payload = " ".join(args)
            payload_arguments = payload.split("|")
            if len(payload_arguments) < 2:
                message = payload_arguments [0]
                await ctx.send(message)
                await ctx.message.delete()
            else: 
                message = payload_arguments [0]
                channel_name = payload_arguments[1]
                try:
                    channel = self.bot.get_channel(int(channel_name))
                except ValueError:
                    channel = self.bot.get_channel(int(channel_name.strip()[2:][:-1]))
                if channel != None:
                    await channel.send(message)

    #Events
    @commands.Cog.listener()
    async def on_message(self, message):
        '''
        Allows bot to reply to social messages 
        '''
        author = message.author
        content = message.content.lower()
        channel = message.channel
            
        # we do not want the bot to reply to itself
        if author.id == self.bot.user.id:
            return

        if (('hello' in content) or ('hi' in content) or ('hey' in content)) and (("makernaut" in content) or ("makernaut!" in content)):
            try:
                print('Inside Bot Context: ' + message.content)
                emoji = '\N{WHITE HEAVY CHECK MARK}'
                await message.add_reaction(emoji)
                await message.channel.send('Hello {0.author.mention}'.format(message))
            except discord.HTTPException:
                # sometimes errors occur during this, for example
                # maybe you dont have permission to do that
                # we dont mind, so we can just ignore them
                pass   
        if 'good bot' in content:
            try:
                emoji = '\N{SPARKLING HEART}'
                await message.add_reaction(emoji)
                await message.channel.send('Aww, thanks {0.author.mention}. Good human!'.format(message))

            except discord.HTTPException:
                # sometimes errors occur during this, for example
                # maybe you dont have permission to do that
                # we dont mind, so we can just ignore them
                pass 
        if 'bad bot' in content:
            try: 
                await message.channel.send('https://tenor.com/view/pedro-monkey-puppet-meme-awkward-gif-15268759')
            except discord.HTTPException:
                # sometimes errors occur during this, for example
                # maybe you dont have permission to do that
                # we dont mind, so we can just ignore them
                pass 
        
        url_pattern = r'''(?xi)
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
        gifs_pattern = r'^https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpg|gif|png)$|\W*(tenor.com)\W*|\W*(gfycat.com)\W*|\W*(imgur.com)\W*|\W*(giphy.com)\W*'
        sus_nitro_pattern = r'\W*(discord)\W*|\W*(nitro)\W*'
        real_nitro_pattern = r'\W*(discord.com)\W*|\W*(discord.gg)\W*|\W*(discordapp.com)\W*'

        matching_url = re.findall(pattern=url_pattern, string=content)
        matching_gifs = re.findall(pattern=gifs_pattern, string=content)
        matching_sus_nitro = re.findall(pattern=sus_nitro_pattern, string=content) 
        matching_real_nitro = re.findall(pattern=real_nitro_pattern, string=content) 

        if matching_url:

            if matching_real_nitro:
                pass # Real Discord link

            elif matching_sus_nitro:

                if (matching_gifs):
                    pass # Kinda sus, but just media

                else: 
                    # Most likely a scam
                    await message.delete()

                    SPAM_REPORT_TITLE = "Pontential Spam Removed"
                    SPAM_REPORT_DESCRIPTION = f"" #tags moderators
                    RED_HEX = 0xD2222D  
                    embed_response = discord.Embed(title=SPAM_REPORT_TITLE, description=SPAM_REPORT_DESCRIPTION, color=RED_HEX)
                    embed_response.add_field(name="Author", value= f"{author.mention}", inline=False)
                    embed_response.add_field(name="Original Message", value=f'{message.content}', inline=False)                     
                    
                    isProtected = False
                    for role in author.roles:
                        if role in self.UNPROTECTED_ROLES:
                            pass
                        else:
                            isProtected = True

                    if isProtected:
                        embed_response.add_field(name="Resolution", value= "Message **deleted**!", inline=False)
                    else:
                        embed_response.add_field(name="Resolution", value= "Message **deleted** and member **banned**!", inline=False)
                        await author.ban(reason = f"Automated Ban: Potential Nitro Scam\nMessage:\n {message.content}")
                    await self.log_channel.send(f"<@&{self.MODERATOR_ROLE_ID}>")
                    await self.log_channel.send(embed=embed_response)

            else:
                pass # Random URL

def setup(bot):
    bot.add_cog(BotContext(bot)) 
    