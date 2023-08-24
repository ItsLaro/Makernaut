import discord
from discord.ext import commands
from ..models.guild import GuildState


class GuildLevelManager():
    def __init__(self, bot):
        self.bot = bot
        self.GUILD_ID: int = 245393533391863808
        self.GUILDS_CATEGORY_ID: discord.CategoryChannel.id = '1065808460492574730' if config.isProd else '1131014053322576013' 
        self.GUILDS_CATEGORY: discord.CategoryChannel = discord.utils.get(self.GUILD.categories, id=self.GUILDS_CATEGORY_ID)
        self.PARTY_FORUM_ID: discord.ForumChannel.id = '1067996331727134780' if config.isProd else '1131014260336627813'
        self.PARTY_FORUM: discord.ForumChannel = discord.utils.get(self.GUILD.categories, id=self.PARTY_CHANNEL_ID) 
    
    async def promote_party(self, party_id: int) -> :
        pass

    async def promote_guild(self, guild_id: int):
        pass

    async def demote_guild(self, guild_id: int):
        pass