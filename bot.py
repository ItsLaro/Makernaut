import os
import traceback
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.app_commands import command
import config 
from cogs.verification import InitiateControls as VerificationInitiateControls
from cogs.guilds import InitiateControls as PartyInitiateControls
from cogs.guilds import DecisionControls

load_dotenv()
secret_key = os.getenv("BOT_KEY")

class Gui(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        prefix = commands.when_mentioned_or('?')
        super().__init__(command_prefix =prefix , intents=intents)

    async def setup_hook(self):
        self.add_view(VerificationInitiateControls())
        self.add_view(PartyInitiateControls())
        # self.add_view(DecisionControls('','','',''))

    async def on_ready(self):
        
        print(f'{"Prod" if config.isProd else "Test"} Bot is Online~\n{bot.user.name}, (ID: {bot.user.id})\n')
        
        #Loads cogs
        print('⚙️ Loading cogs: ⚙️')
        for filename in os.listdir('./cogs'):
            try:
                if filename.endswith('.py'):
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'- {(filename[:-3]).title()} functionality loaded ✅')
            except Exception:
                    tb = traceback.format_exc()
                    print(f'- {(filename[:-3]).title()} failed to load ❌ due to "{tb}""')
        
        #Set status
        await bot.change_presence(status = discord.Status.online, activity=discord.Game("Ready to Help!"))
        print(f'\nAll set! 🚀\n')
            
    async def on_disconnect(self):
        print('Bot Disconnected...')

    async def on_error(self, error):
            print("Oh No!")

bot = Gui()

@bot.hybrid_group(name='core', group='core', description="Core commands")
async def core(self, ctx):
    pass

@core.command(name='sync', with_app_command=True, description="Sync the list of commands")
@commands.has_permissions(administrator=True)
async def sync(ctx: commands.Context):
    await bot.tree.sync()
    print('Command Tree Synced! 🔄')
    await ctx.reply('Command Tree Synced! 🔄', ephemeral=True)

if __name__ == "__main__":
    bot.run(secret_key)