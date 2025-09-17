import discord
from discord.ext import commands
from discord import ui
from helpers.notion import NotionDB

class ShellFAQ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notion = NotionDB()
        bot.add_listener(self.on_thread_create, 'on_thread_create')
    
    # attempts to respond to the description of a user's thread question
    # by searching a notion database filled with questions related to Shell
    async def on_thread_create(self, thread: discord.Thread):
        # only respond to new threads in the specified forum channel
        SPECIFIC_FORUM_CHANNEL_ID = 1413314716092207257
        if thread.parent and thread.parent.id == SPECIFIC_FORUM_CHANNEL_ID:
            # fetch the starter message (the initial post/question)
            try:
                starter_message = await thread.fetch_message(thread.id)
            except Exception:
                starter_message = None
            if starter_message and not starter_message.author.bot:
                question = starter_message.content.strip()

                # search the notion database for the question / answer
                if question:
                    answer = self.notion.search_faq(question)
                    # if found, send an embed with the answer to their question
                    if answer:
                        embed = discord.Embed(
                            title=question,
                            description=answer,
                            color=discord.Color.green()
                        )
                        await thread.send(embed=embed, view=FAQView(question, answer))
                    # if no answer was retrieved from the db then the user
                    # is given the option to ping a support role to assist them
                    else:
                        embed = discord.Embed(
                            title= "Couldn't Answer your Question",
                            description="Sorry, I couldn't help you find an answer for that. Please choose an option that most accurately represents the type of question you have and a ShellHacks team member will assist you soon!",
                            color=discord.Color.yellow()
                        )

                        await thread.send(embed=embed, view=FAQViewFail(question))

class FAQView(ui.View):
    def __init__(self, question, answer):
        super().__init__(timeout=120)
        self.question = question
        self.answer = answer

    # if the user's question was not answered they can request extra help
    # to ping a supporting role in the discord
    @ui.button(label="Still need help", style=discord.ButtonStyle.danger)
    async def not_helpful(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="Couldn't Answer your Question",
            description="Sorry, I couldn't help you find an answer for that. Please choose an option that most accurately represents the type of question you have and a ShellHacks team member will assist you soon!",
            color=discord.Color.yellow()
        )
        button.disabled = True # disables button after being clicked
        await interaction.response.send_message(embed=embed, view=FAQViewFail(self.question))
        await interaction.message.edit(view=self)
        self.stop()
        
async def setup(bot):
    await bot.add_cog(ShellFAQ(bot))

# provides the user with the option to ping a particular 
# type of help role regarding their question
class FAQViewFail(ui.View):
    def __init__(self, question):
        super().__init__(timeout=120)
        self.question = question

    @ui.button(label="🐚 Organizers Core", style=discord.ButtonStyle.primary)
    async def ping_organizers_core(self, interaction: discord.Interaction, button: ui.Button):
        ORGANIZERS_CORE_ROLE_ID = 1133217785149927485
        await interaction.response.send_message(f"<@&{ORGANIZERS_CORE_ROLE_ID}> Someone needs help with: '{self.question}'", ephemeral=False)
        self.disable_all_buttons()
        await interaction.message.edit(view=self)
        self.stop()

    @ui.button(label="🤝 Organizer", style=discord.ButtonStyle.success)
    async def ping_organizer(self, interaction: discord.Interaction, button: ui.Button):
        ORGANIZER_ROLE_ID = 888960305693069402
        await interaction.response.send_message(f"<@&{ORGANIZER_ROLE_ID}> Someone needs help with: '{self.question}'", ephemeral=False)
        self.disable_all_buttons()
        await interaction.message.edit(view=self)
        self.stop()

    @ui.button(label="👨‍💻 Discord Support", style=discord.ButtonStyle.danger)
    async def ping_discord_support(self, interaction: discord.Interaction, button: ui.Button):
        DISCORD_SUPPORT_ROLE_ID = 1150551214845603880
        await interaction.response.send_message(f"<@&{DISCORD_SUPPORT_ROLE_ID}> Someone needs help with: '{self.question}'", ephemeral=False)
        self.disable_all_buttons()
        await interaction.message.edit(view=self)
        self.stop()

    @ui.button(label="🏆 MLH", style=discord.ButtonStyle.secondary)
    async def ping_mlh(self, interaction: discord.Interaction, button: ui.Button):
        MLH_ROLE_ID = 1152126734309785610
        await interaction.response.send_message(f"<@&{MLH_ROLE_ID}> Someone needs help with: '{self.question}'", ephemeral=False)
        self.disable_all_buttons()
        await interaction.message.edit(view=self)
        self.stop()

    
    # disables all buttons for FAQViewFail when one is clicked
    def disable_all_buttons(self):
        for child in self.children:
            if isinstance(child, ui.Button):
                child.disabled = True


