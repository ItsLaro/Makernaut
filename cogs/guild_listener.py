import discord
from discord.ext import commands
from models.guild import MessageMetadata, guild, guildState
from db.database import Database
import config

db = Database()

class GuildActivityListener(commands.Cog):
    """
    Cog that listens to activity in guild/party channels and logs them into SQL.

    Args:
        bot (discord.Client): The bot client that's currently running.

    Attributes:
        bot (discord.Client): The bot client that's currently running.
        guild_id (int): ID of the guild.
        guild (discord.guild): guild object retrieved from the bot.
        guilds_category_id (discord.CategoryChannel.id): Category ID for the guilds.
        guilds_category (discord.CategoryChannel): Category object for the guilds.
        party_forum_id (discord.ForumChannel.id ): Forum ID for the party.
        party_forum (discord.ForumChannel): Forum object for the party.
    """
    def __init__(self, bot):
        self.bot = bot
        self.guild_id: int = 245393533391863808
        self.guild = self.bot.get_guild(self.guild_id)
        self.guilds_category_id: discord.CategoryChannel.id = (
            '1065808460492574730' if config.isProd else '1131014053322576013'
        )
        self.guilds_category: discord.CategoryChannel = discord.utils.get(
            self.guild.categories, id=self.guilds_category_id
        )
        self.party_forum_id: discord.ForumChannel.id = (
            '1067996331727134780' if config.isProd else '1131014260336627813'
        )
        self.party_forum: discord.ForumChannel = discord.utils.get(
            self.guild.categories, id=self.PARTY_CHANNEL_ID
        )

    @commands.Cog.listener()
    async def on_party_channel_create(self, channel_created: discord.Channel) -> None:
        """
        Listens for new forum posts in our party forum, if one is created
        we wil add them to SQL
        
        Args:
            new_party (discord.Channel): The new party that was created.
        """
        if isinstance(
            channel_created,
            discord.TextChannel
            ) and (channel_created.category_id == self.party_forum_id):
            new_party: guild = {
                'channel_id': None,
                'forum_post_id': channel_created.id,
                'level': 0,
                'guild_state': guildState.NEW
            }
            return db.set_guild(new_party)

    @commands.Cog.listener()
    async def on_message(self, listened_message: discord.Message) -> None:
        """
        Listens to messages within our guild and party channels
        If one is created, strip down data and send to SQL.

        Args:
            message (discord.Message): The new message that was sent.
        """
        if listened_message.channel.category_id in [self.party_forum_id,
                                                    self.guilds_category_id]:
            new_message: MessageMetadata = {
                'timestamp': listened_message.created_at,
                'message_location_id': listened_message.id,
                'message_location_type': listened_message.type,
                'user_id': listened_message.author.id
        }
        return db.set_message(
            listened_message.channel.id,
            listened_message.channel.type.name,
            new_message
        )

def setup(bot):
    """
    Function required for cogs. Adds the cog to the bot.

    Args:
        bot (discord.Client): The bot client that's currently running.
    """
    bot.add_cog(GuildActivityListener(bot))
