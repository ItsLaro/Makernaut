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
        new_party_embed = discord.Embed(description=self.guild_description, color=BLUE)
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

class NewPartyModal(Modal, title='Create a Guild!'):
    name = TextInput(
        style=discord.TextStyle.short,
        label="Guild Name",
        required=True,
        placeholder="Must be something meaningful and straightforward",
        min_length=3
    )

    description = TextInput(
        style=discord.TextStyle.long,
        label="Guild Description",
        required=True,
        max_length=1000,
        min_length=64,
        placeholder="What is this Guild about? This will be public and sent as the first message in the channel"
    )

    async def on_submit(self, interaction: discord.Interaction):
        # townhall_channel = interaction.guild.get_channel(1066464344231125083 if config.isProd else 1069736956738666506)
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
        pass
        
    @app_commands.command(name="initiate", description="Sow the seeds to a new Guild")
    async def initiate(self, interaction: discord.Interaction):
        await interaction.response.send_modal(NewPartyModal()) 

async def setup(bot):
    await bot.add_cog(Guild(bot))