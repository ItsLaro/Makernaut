import discord
from discord.ext import commands
import config

class FeedbackView(discord.ui.View):
    """A view to get feedback on the KB answer."""
    def __init__(self, bot):
        super().__init__(timeout=300) # 5 minute timeout
        self.bot = bot
        self.feedback_given = False

    @discord.ui.button(label="Yes, this was helpful!", style=discord.ButtonStyle.success)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.feedback_given:
            await interaction.response.send_message("You've already provided feedback.", ephemeral=True)
            return
            
        self.feedback_given = True
        button.disabled = True
        self.children[1].disabled = True # Disable the 'No' button
        await interaction.message.edit(view=self)
        await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)
        self.stop()

    @discord.ui.button(label="No, I need more help.", style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.feedback_given:
            await interaction.response.send_message("You've already provided feedback.", ephemeral=True)
            return

        self.feedback_given = True
        button.disabled = True
        self.children[0].disabled = True # Disable the 'Yes' button
        await interaction.message.edit(view=self)
        
        # Let the user know we're creating a ticket
        await interaction.response.send_message("I'm sorry the answer wasn't helpful. Please select a category to create a support ticket.", ephemeral=True)

        # Trigger the support ticket flow
        support_cog = self.bot.get_cog('SupportTickets')
        if support_cog:
            # Use the original message that triggered the bot
            await support_cog.show_category_buttons(interaction.message)
        
        self.stop()

class KBResponder(commands.Cog):
    """
    Main message handler that coordinates KB search and support tickets
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.UPE_GUILD_ID = config.UPE_GUILD_ID
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages that might need KB responses"""
        
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Only respond in the correct guild
        if message.guild and message.guild.id != self.UPE_GUILD_ID:
            return
        
        # Only respond to mentions or DMs
        if not (self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel)):
            return
        
        # Get the question from the message
        question = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
        
        if not question:
            return
        
        # Try to search the knowledge base first
        notion_kb = self.bot.get_cog('NotionKB')
        if notion_kb:
            kb_result = await notion_kb.search_kb(question)
            
            if kb_result:
                # Found answer in KB
                embed = notion_kb.format_kb_response(kb_result)
                await message.channel.send(embed=embed, view=FeedbackView(self.bot))
                return
            print("No KB result found.")

        # No KB answer found - show support ticket options
        support_tickets = self.bot.get_cog('SupportTickets')
        if support_tickets:
            await support_tickets.show_category_buttons(message)

async def setup(bot):
    await bot.add_cog(KBResponder(bot))