import discord
import os
from discord.ext import commands
import config

class CategoryView(discord.ui.View):
    """View with buttons for different support categories"""
    
    def __init__(self, support_role_id):
        super().__init__(timeout=300)  # 5 minute timeout
        self.support_role_id = support_role_id
    
    @discord.ui.button(label='🔧 Technical Issues', style=discord.ButtonStyle.red)
    async def technical_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Technical Issues", "🔧")
    
    @discord.ui.button(label='📝 Registration Issues', style=discord.ButtonStyle.blurple)
    async def registration_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Registration Issues", "📝")
    
    @discord.ui.button(label='ℹ️ General Information', style=discord.ButtonStyle.green)
    async def general_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "General Information", "ℹ️")
    
    async def create_ticket(self, interaction: discord.Interaction, category: str, emoji: str):
        """Create a support ticket for the selected category"""
        
        # Create embed for ticket confirmation
        embed = discord.Embed(
            title=f"{emoji} Support Ticket Created",
            description=f"**Category:** {category}\n**User:** {interaction.user.mention}",
            color=0xffa500  # Orange color
        )
        embed.add_field(
            name="What happens next?",
            value="Our support team has been notified and will assist you shortly!",
            inline=False
        )
        embed.set_footer(text="Support Ticket System")
        
        # Ping the support team
        support_message = f"🎫 **New Support Ticket**\n"
        support_message += f"**Category:** {category}\n"
        support_message += f"**User:** {interaction.user.mention}\n"
        support_message += f"**Original Question:** Check the message above\n\n"
        support_message += f"<@&{self.support_role_id}> - Please assist this user!"
        
        # Respond to the interaction
        await interaction.response.edit_message(
            content=support_message,
            embed=embed,
            view=None  # Remove the buttons
        )
        
        # Create a thread for the ticket (optional)
        try:
            thread = await interaction.message.create_thread(
                name=f"{category} - {interaction.user.display_name}",
                auto_archive_duration=1440  # 24 hours
            )
            await thread.send(f"Support thread created for {interaction.user.mention}. Please describe your issue in detail here.")
        except:
            # If thread creation fails, just continue without it
            pass

class SupportTickets(commands.Cog):
    """
    Handles support ticket creation when KB doesn't have answers
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.UPE_GUILD_ID = config.UPE_GUILD_ID
        self.support_role_id = config.SUPPORT_ROLE_ID

    async def show_category_buttons(self, message):
        """Show category selection buttons to the user"""
        
        embed = discord.Embed(
            title="🎫 No Knowledge Base Answer Found",
            description="I couldn't find an answer to your question in our knowledge base. Please select the most appropriate category below, and our support team will assist you!",
            color=0xff6b6b  # Red color
        )
        embed.add_field(
            name="📂 Categories Available:",
            value="🔧 **Technical Issues** - API, development, infrastructure\n📝 **Registration Issues** - Account, authentication, permissions\nℹ️ **General Information** - Events, resources, policies",
            inline=False
        )
        embed.set_footer(text="Click a button below to create a support ticket")
        
        view = CategoryView(self.support_role_id)
        
        await message.reply(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(SupportTickets(bot))