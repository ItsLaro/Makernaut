import discord
from discord.ext import commands
from discord import app_commands
import config
from discord.ui import TextInput, Modal, Select, Button, View
from discord import SelectOption, ActionRow, ButtonStyle
import config
import traceback
import inspect

#Colors HEX
BLUE = 0x3895D3
YELLOW = 0xFFBF00  

class DecisionControls (View):
    isApproved : bool = None
    decisionByUser = None

    def __init__(self, guild_name, guild_description, guild_author, message_embed, timeout=None):
        self.guild_name = guild_name
        self.guild_description = guild_description
        self.guild_author = guild_author
        self.message_embed = message_embed
        super().__init__(timeout=timeout)

    async def decide_and_disable(self):
        for item in self.children:
            item.disabled = True

        message_embed = self.message_embed    
        message_embed.remove_field(index=3)
        message_embed.add_field(name="Status:", value=f'{"✅ Approved" if self.isApproved else "❌ Rejected"} by {self.decisionByUser.mention}', inline=False)
        
        await self.message.edit(embed=message_embed, view=self)

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        parties_channel = interaction.guild.get_channel(1067996331727134780 if config.isProd else 1071815435714043996)

        self.isApproved = True
        self.decisionByUser = interaction.user
        self.stop()
        await interaction.response.send_message(
            f"You've **approved** the request for the *{self.guild_name} Guild*, make sure that a thread has been properly created in {parties_channel.mention}", 
            ephemeral=True
        ) 

        #response in parties
        new_party_message = f"Hey, this is the start of {self.guild_name} Guild! In {self.guild_author.mention}'s own words: "
        new_party_embed = discord.Embed(description=self.guild_description, color=discord.Colour.random())
        new_party_embed.set_author(name=self.guild_author.display_name.split()[0], icon_url=self.guild_author.avatar.url)
        await parties_channel.create_thread(name=self.guild_name, content=new_party_message, embed=new_party_embed)       

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.isApproved = False
        self.decisionByUser = interaction.user
        self.stop()
        await interaction.response.send_message(
            f"You've **rejected** the request for the *{self.guild_name} Guild*. Let's reach out to {self.guild_author.mention} to see how they can improve their initiative!", 
            ephemeral=True
        )

class InitiateControls (View):
    @discord.ui.button(label="Start your Own Guild", style=discord.ButtonStyle.primary)
    async def initiate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NewPartyModal()) 

class NewPartyModal(Modal, title='Create a Guild!'):
    name = TextInput(
        style=discord.TextStyle.short,
        label="Guild Name (Please omit the word 'Guild')",
        required=True,
        placeholder="Something meaningful but clear and straightforward",
        min_length=3
    )

    description = TextInput(
        style=discord.TextStyle.long,
        label="Guild Description (This will be public)",
        required=True,
        max_length=1000,
        min_length=128,
        placeholder="What is it about? What will you do together? In-person or Online? Technical or Fun? Be descriptive!"
    )

    async def on_submit(self, interaction: discord.Interaction):
        parties_channel = interaction.guild.get_channel(1067996331727134780 if config.isProd else 1071815435714043996)

        embed_response = discord.Embed(title="New Guild Application",
                              description="Review carefully and react below to approve or reject. Approving will automatically create a public thread for this Guild.",
                              color=YELLOW)
        embed_response.add_field(name="Guild Name:", value=f'"{self.name.value}"', inline=False)
        embed_response.add_field(name="Guild Description:", value=f'"{self.description.value}"', inline=False)
        embed_response.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed_response.add_field(name="Founder / Submitter:", value=f'{interaction.user.mention}', inline=False)
        embed_response.add_field(name="Status:", value=f'⏺ Pending', inline=False)

        controls = DecisionControls(self.name.value, self.description.value, interaction.user, embed_response, timeout=None)

        moderator_channel = interaction.guild.get_channel(745092495725297825 if config.isProd else 1065042159176273989)
        moderator_message = await moderator_channel.send(embed=embed_response, view=controls)

        controls.message = moderator_message 

        await interaction.response.send_message(
            f"Thank you for you interest, {interaction.user.mention}! You should see the start of your Guild in the form of a thread in the {parties_channel.mention} channel in the next *24 hours* following approval. I'll try to DM you!", 
            ephemeral=True
        )

        await controls.wait()
        await controls.decide_and_disable()

    async def on_error(self, interaction: discord.Interaction, error : Exception):

        traceback.print_exception(error, error.__traceback__, 1)

        await interaction.response.send_message(f"Oops... There was an error completing your request. {interaction.user.mention}, please try again later or reach out to a Moderator!", ephemeral=True)

class Guild(commands.GroupCog, name="guild"):

    def __init__(self, bot) -> None:
        self.bot = bot

    async def cog_load(self):
        TOWNHALL_CHANNEL_ID = 1066464344231125083 if config.isProd else 1069736956738666506
        townhall_channel = self.bot.get_channel(TOWNHALL_CHANNEL_ID)

        PARTIES_CHANNEL_ID = 1067996331727134780 if config.isProd else 1071815435714043996
        parties_channel = self.bot.get_channel(PARTIES_CHANNEL_ID)

        # We clean channel for stale messages and resend a new one
        async for message in townhall_channel.history():
            if message.author.id == self.bot.user.id:
                await message.delete()

        # Send a new Guild start message
        embed_title = "Let's Build Community!"
        embed_description = "_Guilds_ are subcommunities, by members for members, that revolve around a particular focus or interest. These can range from learning and honing a particular skill or simply to hang out, make friends, and vibe along."

        embed = discord.Embed(title=embed_title, description=embed_description, color=discord.Colour.blurple())
        embed.add_field(name="How can I join?", value=f'You can check out _established_ Guilds by selecting them on the <id:customize> menu or visit the rising ones forming over at the {parties_channel.mention} channel', inline=False)
        embed.add_field(name="What are _Parties_?", value=f"A Party is just a friendly term for a _level 0_ Guild that has yet to be _established_ and therefore has yet to be officially endorsed by INIT.", inline=False)
        embed.add_field(name="What are Levels?", value=f'Levels are indicative of the size and scale of your Guild. The higher the level of your guild, the more support and benefits it will receive.', inline=False)
        embed.add_field(name="Level 3", value=f'TBA', inline=True)
        embed.insert_field_at(3, name="Level 2", value=f'TBA', inline=True)
        embed.insert_field_at(3, name="Level 1", value=f'TBA', inline=True)

        embed.add_field(name="What are the requirements?", value="The are requirements that should be reached and _maintained_ to progress through each level", inline=False)
        embed.add_field(name="Level 3", value=f'TBA', inline=True)
        embed.insert_field_at(7, name="Level 2", value=f'TBA', inline=True)
        embed.insert_field_at(7, name="Level 1", value=f'TBA', inline=True)

        embed.add_field(name="What are the benefits?", value="Many many benefits, but the true reward is the friendships we will make along the way", inline=False)

        embed.add_field(name="What happens if I fail?", value="There's **no** such thing as failure with Guilds. A Guild is a hands off initiative from members by members. If activity fades away to the point where it no longer qualifies to be _established_, the Guild will _vanish_. Don't let that discourage you however! You can always try again!", inline=False)

        embed.add_field(name="Want to start your own?", value=f'If you want to lead a Guild or have a great idea, click the button below to get started.', inline=False)

        controls = InitiateControls(timeout=None)
        
        self.bot_intro_message = await townhall_channel.send(embed=embed, view=controls)

        
    @app_commands.command(name="initiate", description="Sow the seeds to a new Guild")
    async def initiate(self, interaction: discord.Interaction):
        await interaction.response.send_modal(NewPartyModal()) 

async def setup(bot):
    await bot.add_cog(Guild(bot))