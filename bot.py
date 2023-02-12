import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.app_commands import command
import config 

load_dotenv()
secret_key = os.getenv("BOT_KEY")

command_prefix = '?'
intents = discord.Intents().all()
bot = commands.Bot(command_prefix, intents=intents, help_command=None)

MODERATOR_ROLE_ID = 399551100799418370 if config.isProd else 1065042154407338039

@bot.event
async def on_ready():
    
    print(f'{"Prod" if config.isProd else "Test"} Bot is Online~\n{bot.user.name}, (ID: {bot.user.id})\n')
    
    #Loads cogs
    print('⚙️ Loading cogs: ⚙️')
    for filename in os.listdir('./cogs'):
        try:
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'- {(filename[:-3]).title()} functionality loaded ✅')
        except Exception as error:
                print(f'- {(filename[:-3]).title()} failed to load ❌ due to "{error}""')
    
    #Set status
    await bot.change_presence(status = discord.Status.online, activity=discord.Game("Ready to Help!"))
    print(f'\nAll set! 🚀\n')
        
@bot.event
async def on_disconnect():
    print('Bot Disconnected...')

# @bot.tree.error
# async def on_error(interaction, error):
#     await interaction.channel.send(error, ephemeral=True)

@bot.hybrid_group(name='core', group='core', description="Core commands")
async def core(self, ctx):
    pass

@core.command(name='sync', with_app_command=True, description="Sync the list of commands")
@commands.has_permissions(administrator=True)
async def sync(ctx: commands.Context):
    await bot.tree.sync()
    print('Command Tree Synced! 🔄')
    await ctx.reply('Command Tree Synced! 🔄', ephemeral=True)

# @core.command(name='load', with_app_command=True, description="Load a specified cog")
# @commands.has_permissions(administrator=True)
# async def load(ctx: commands.Context, extension: str):
#     bot.load_extension(f'cogs.{extension}')
#     await ctx.reply(f'{extension.title()} cog has been loaded', ephemeral=True)

# @core.command(name='unload', with_app_command=True, description="Unload a specified cog")
# @commands.has_permissions(administrator=True)
# async def unload(ctx: commands.Context, extension: str):
#     bot.unload_extension(f'cogs.{extension}')
#     await ctx.repy(f'{extension.title()} cog was unloaded', ephemeral=True)

# @core.command(name='reload', with_app_command=True, description="Reload all cogs")
# @commands.has_permissions(administrator=True)
# async def reload(ctx: commands.Context):
#     try:
#         for filename in os.listdir('./cogs'):
#             if filename.endswith('.py'):
#                 bot.unload_extension(f'cogs.{filename[:-3]}')
#                 bot.load_extension(f'cogs.{filename[:-3]}')
#                 print(f'- {(filename[:-3]).title()} functionality reloaded')
#         await ctx.reply(f'Cogs reloaded succesfully', ephemeral=True)
#         print(f'Cogs reloaded succesfully\n')
#     except Exception:
#         await ctx.reply(f"Something's not right...", ephemeral=True)
#         print(Exception)

if __name__ == "__main__":
    bot.run(secret_key)