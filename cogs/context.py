import discord
from discord.ext import commands

class BotContext(commands.Cog):

    '''
    Behaviour of the bot and its sorroundings
    '''
    def __init__(self, bot):
        self.bot = bot
        self.EBOARD_BOTSPAM_CHANNEL_ID = 626183709372186635
        self.GENERAL_BOTSPAM_CHANNEL_ID = 401577290863083531

    #Commands
    @commands.command()
    async def speak(self, ctx, *args):
        '''
        Gui will repeat after you.Ex: ?speak Hello World!\nYou can also specify the channel after a `|`.\nEx: ?speak Hello users in another channel! | 808635094373761064
        '''        
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

        allowed_channel_ids = [self.EBOARD_BOTSPAM_CHANNEL_ID, self.GENERAL_BOTSPAM_CHANNEL_ID]

        author = message.author
        content = message.content.lower()
        channel = message.channel

        if channel.id in allowed_channel_ids: 
            
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

def setup(bot):
    bot.add_cog(BotContext(bot)) 
    