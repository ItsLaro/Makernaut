import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
secret_key = os.getenv("BOT_KEY")

command_prefix = '!'
intents = discord.Intents().all()
bot = commands.Bot(command_prefix, intents=intents)

@bot.event
async def on_ready():
    
    print(f'Bot is Online~\n{bot.user.name}, (ID: {bot.user.id})\n')
    
    #Loads cogs
    print('Loading cogs:')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'- {(filename[:-3]).title()} commands loaded')
    
    #Set status
    await bot.change_presence(status = discord.Status.online, activity=discord.Game("Ready to Help!"))
    print(f'All set! 🚀\n')
        
@bot.event
async def on_disconnect():
    print('Bot Disconnected...')

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension.title()} cog has been loaded')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension.title()} cog was unloaded')

@bot.command()
async def reload(ctx):
    try:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                bot.unload_extension(f'cogs.{filename[:-3]}')
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'- {(filename[:-3]).title()} commands reloaded')
        await ctx.send(f'Cogs reloaded succesfully')
        print(f'Cogs reloaded succesfully\n')
    except Exception:
        await ctx.send(f"Something's not right...")
        print(Exception)

if __name__ == "__main__":
    bot.run(secret_key)