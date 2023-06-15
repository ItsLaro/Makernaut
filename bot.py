import os
import traceback
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import SelectOption, PartialEmoji
import config 
from cogs.verification import InitiateControls as VerificationInitiateControls
from cogs.guilds import InitiateControls as PartyInitiateControls
from cogs.alumni import SelectView
from helpers.emojis import alphabet

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
        company_sorted_combined_options_and_roles = await self.fetch_combined_options_and_roles_via_role_prefix('Alumni Company - ')
        self.add_view(SelectView(company_sorted_combined_options_and_roles))
        profession_sorted_combined_options_and_roles = await self.fetch_combined_options_and_roles_via_role_prefix('Alumni Role - ')
        self.add_view(SelectView(profession_sorted_combined_options_and_roles))

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

    async def fetch_combined_options_and_roles_via_role_prefix(self, prefix):
        UPE_GUILD_ID = 245393533391863808 if config.isProd else 1065042153836912714
        upe_guild = await bot.fetch_guild(UPE_GUILD_ID)
        roles = await upe_guild.fetch_roles()
        ## Company Roles ##
        company_roles=[]
        prefix_length = len(prefix)
        for role in roles:
            if role.name.startswith(prefix):
                role_name = role.name[prefix_length:]
                emoji_codepoint = alphabet[role_name[0].upper()]
                company_roles.append(role)
        
        sorted_company_roles = sorted(company_roles, key=lambda entry: entry.name.lower())  
        company_options=[]
        for index, role in enumerate(sorted_company_roles):
            role_name = role.name[prefix_length:]
            company_options.append(SelectOption(label=role_name, emoji=PartialEmoji(name=emoji_codepoint, animated=False), value=index))
        company_sorted_combined_options_and_roles = [{'option': option, 'role': role} for option, role in zip(company_options, sorted_company_roles)]
        return company_sorted_combined_options_and_roles

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