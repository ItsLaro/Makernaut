import discord
from discord.ext import commands

class BotContext(commands.Cog):

    '''
    Behaviour of the bot and its sorroundings
    '''
    def __init__(self, bot):
        self.bot = bot


    #Events
    @commands.Cog.listener()
    async def on_message(self, message):
        '''
        Allows bot to reply to social messages 
        '''
        # we do not want the bot to reply to itself
        author = message.author
        content = message.content.lower()
        channel = message.channel

        if channel.id == 789520848049537055: 
        
            if author.id == self.bot.user.id:
                return

            if (('hello' in content) or ('hi' in content)) and "makernaut" in content:
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
    