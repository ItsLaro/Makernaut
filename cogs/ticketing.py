import discord
from discord.ui import View
from discord.ext import commands
import config

# Channel IDs
SUPPORT_CHANNEL_ID = 1421168182420443208

# Role IDs
MODERATOR_ROLE_ID = 399551100799418370  if config.isProd else 1065042154407338039
MENTOR_ROLE_ID = 888959725037846578 if config.isProd else 1065042154289897544
ORGANIZER_ROLE_ID = 399558426511802368 if config.isProd else 1065042154289897546
MLH_ROLE_ID = 1152126734309785610 if config.isProd else 1152165574760202291
DISCORD_SUPPORT_ROLE_ID = 1150551214845603880 if config.isProd else 1150550766927495309


class TicketControls(View):
    """
    A Discord View that provides ticket creation functionality.
    Creates private threads for different types of support requests.
    """
    
    def __init__(self):
        super().__init__(timeout=None)
        self.MODERATOR_ROLE_ID = MODERATOR_ROLE_ID
        self.MENTOR_ROLE_ID = MENTOR_ROLE_ID
        self.ORGANIZER_ROLE_ID = ORGANIZER_ROLE_ID
        self.MLH_ROLE_ID = MLH_ROLE_ID
        self.DISCORD_SUPPORT_ROLE_ID = DISCORD_SUPPORT_ROLE_ID

    async def create_private_thread(self, interaction, reason, cced_role):
        """
        Creates a private thread for a ticket request.
        
        Args:
            interaction: Discord interaction object
            reason: String describing the ticket type
            cced_role: Discord role to mention in the thread
        """
        moderator_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)
        thread = await interaction.channel.create_thread(
            name=f"{interaction.user.nick.split()[0] if interaction.user.nick else interaction.user.name.split()[0] }'s {reason} Ticket",
            reason=reason
        )
        message = f'''
{interaction.user.mention}, this is your private thread for {reason}. This is **only** visible by:
- **YOU**
- {cced_role.mention}s
- Our admins and {moderator_role.mention}s

Someone will be here to help you shortly. <a:wumpusblob:799276931294953482>
        '''
        await thread.send(message)
        await interaction.response.send_message(
            f"A thread for your **{reason}** ticket has been created! Find it under this channel in the [Channel List on the left](https://media.discordapp.net/attachments/1152135403332194346/1152271772155125860/image.png?width=568&height=213) or by clicking the [Threads Icon at the top-right](https://media.discordapp.net/attachments/1152135403332194346/1152243706892660838/image.png?width=379&height=117)", 
            ephemeral=True
        )

    @discord.ui.button(label='Mentorship Request', style=discord.ButtonStyle.green, emoji="🎫", custom_id='ticketing:mentorship_button')
    async def open_mentorship_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Creates a mentorship request ticket."""
        mentor_role = interaction.guild.get_role(self.MENTOR_ROLE_ID)
        await self.create_private_thread(interaction, "Mentorship Request", mentor_role)

    @discord.ui.button(label='ShellHacks Inquiry', style=discord.ButtonStyle.red, emoji="🏖️", custom_id='ticketing:shellhacks_button')
    async def open_shellhacks_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Creates a ShellHacks inquiry ticket."""
        organizer_role = interaction.guild.get_role(self.ORGANIZER_ROLE_ID)
        await self.create_private_thread(interaction, "Shellhacks Inquiry", organizer_role)

    @discord.ui.button(label='Ask MLH', style=discord.ButtonStyle.gray, emoji="🎟️", custom_id='ticketing:mlh_button')
    async def open_mlh_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Creates an MLH support ticket."""
        mlh_role = interaction.guild.get_role(self.MLH_ROLE_ID)
        await self.create_private_thread(interaction, "Ask MLH", mlh_role)

    @discord.ui.button(label='Discord Support', style=discord.ButtonStyle.blurple, emoji="🎴", custom_id='ticketing:discord_button')
    async def open_discord_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Creates a Discord support ticket."""
        discord_role = interaction.guild.get_role(self.DISCORD_SUPPORT_ROLE_ID)
        await self.create_private_thread(interaction, "Discord Support", discord_role)


async def setup_support_channel(bot, support_channel_id=None):
    """
    Sets up the support channel with ticket buttons.
    
    Args:
        bot: Discord bot instance
        support_channel_id: Optional channel ID override
        
    Returns:
        bool: True if message was sent, False if already exists
    """
    if support_channel_id is None:
        support_channel_id = SUPPORT_CHANNEL_ID
    
    support_channel = bot.get_channel(support_channel_id)
    if not support_channel:
        raise ValueError(f"Support channel with ID {support_channel_id} not found")
    
    embed_title = "Get Help!"
    
    # Check if message already exists
    async for message in support_channel.history():
        if message.author.id == bot.user.id and len(message.embeds) > 0 and message.embeds[0].title == embed_title:
            return False  # Message already exists
    
    # Create and send the support message
    support_buttons = TicketControls()
    embed_description = "To open a ticket and get help, choose one of the tickets below. Clicking on a button, will create a private thread with you and the relevant contacts."
    embed_response = discord.Embed(title=embed_title, description=embed_description, color=discord.Color.blurple())
    embed_response.add_field(name='Mentorship Request', value='Connect with a mentor to obtain guidance in your technical endevours.', inline=False)
    embed_response.add_field(name='ShellHacks Inquiry', value='Chat with a member of the Organizing team about a doubt or need.', inline=False)
    embed_response.add_field(name='Ask MLH', value='Ask about any of the [MLH prize categories](https://mlh.link/ShellHacks), resources & technical help, judging criteria, [Code of Conduct](https://mlh.io/code-of-conduct) or anything MLH!', inline=False)
    embed_response.add_field(name='Discord Support', value='Having difficulties here on Discord? Encountered a bug? Report it to us.', inline=False)
    
    await support_channel.send(embed=embed_response, view=support_buttons)
    return True


class Ticketing(commands.Cog):
    """
    Ticketing system cog that provides support ticket functionality.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_load(self):
        """Sets up the support channel with ticket buttons when the cog loads."""
        try:
            await setup_support_channel(self.bot)
        except Exception as e:
            print(f"Failed to setup support channel: {e}")


async def setup(bot):
    """Setup function required for Discord.py cogs."""
    await bot.add_cog(Ticketing(bot))
