import discord
import os
from discord.ext import commands
import config

class CloseTicketView(discord.ui.View):
    """A view with a button to close the support ticket."""
    def __init__(self, support_role_id):
        super().__init__(timeout=None) # Persistent view
        self.support_role_id = support_role_id

    @discord.ui.button(label='Close Ticket', style=discord.ButtonStyle.danger, custom_id='close_ticket_button')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Archives and locks the thread."""
        support_role = interaction.guild.get_role(self.support_role_id)
        
        # Allow users with 'manage_threads' permission OR the support role to close tickets
        has_permission = interaction.user.guild_permissions.manage_threads or (support_role and support_role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message("You do not have permission to close this ticket.", ephemeral=True)
            return

        # Send a confirmation message and archive the thread
        await interaction.response.send_message(f"Ticket closed by {interaction.user.mention}. The thread will now be archived.")
        await interaction.channel.edit(archived=True, locked=True)
        self.stop()

class CategoryView(discord.ui.View):
    """View with buttons for different support categories"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
    
    @discord.ui.button(label='🔧 Technical', style=discord.ButtonStyle.red)
    async def technical_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Technical", "🔧")

    @discord.ui.button(label='📝 Registration', style=discord.ButtonStyle.blurple)
    async def registration_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Registration", "📝")

    @discord.ui.button(label='ℹ️ General', style=discord.ButtonStyle.green)
    async def general_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "General", "ℹ️")
    
    async def create_ticket(self, interaction: discord.Interaction, category: str, emoji: str):
        """Create a support ticket for the selected category"""
        
        # Defer the response to avoid "interaction failed"
        await interaction.response.defer()

        # Get the RoleManager cog
        role_manager = self.bot.get_cog('RoleManager')
        if not role_manager:
            await interaction.followup.send("Error: The RoleManager is not loaded. Please contact an admin.", ephemeral=True)
            return

        # Fetch the role IDs for the selected category
        role_ids = await role_manager.get_roles_for_category(category)
        
        # Fallback to a default role if no specific roles are found
        if not role_ids:
            role_ids = [config.SUPPORT_ROLE_ID]

        # Create a thread for the ticket
        try:
            thread_name = f"{emoji} {category} - {interaction.user.display_name}"
            # We are creating the thread from the message that was replied to
            thread = await interaction.message.create_thread(
                name=thread_name,
                auto_archive_duration=1440  # 24 hours
            )
        except Exception as e:
            await interaction.followup.send(f"Sorry, I couldn't create a support thread. Error: {e}", ephemeral=True)
            return

        # Edit the original reply to confirm thread creation and remove buttons
        embed = discord.Embed(
            title="✅ Support Ticket Created!",
            description=f"Your ticket has been created in {thread.mention}. Please go there to describe your issue.",
            color=0x00ff00
        )
        await interaction.edit_original_response(embed=embed, view=None)
        
        # Create embed for the message inside the thread
        thread_embed = discord.Embed(
            title=f"New {category} Ticket",
            description=f"**User:** {interaction.user.mention}\n**Original Question:** See the message this thread was created from.",
            color=0xffa500
        )
        thread_embed.set_footer(text="A support team member will be with you shortly.")

        # Format the ping message for all relevant roles
        support_ping = " ".join([f"<@&{role_id}>" for role_id in role_ids]) + ", a new ticket has been created."
        
        # Send the initial message in the thread with the close button
        await thread.send(
            content=support_ping,
            embed=thread_embed,
            view=CloseTicketView(role_ids[0]) # Use the first role for close permission
        )

class SupportTickets(commands.Cog):
    """
    Handles support ticket creation when KB doesn't have answers
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.UPE_GUILD_ID = config.UPE_GUILD_ID
        # We still need a default/fallback role ID
        self.support_role_id = config.SUPPORT_ROLE_ID 
        # Add the persistent view so it's active on bot startup
        bot.add_view(CloseTicketView(self.support_role_id))

    async def show_category_buttons(self, message):
        """Show category selection buttons to the user"""
        
        embed = discord.Embed(
            title="🎫 No Answer Found",
            description="I couldn't find an answer to your question. Please select the most appropriate category below, and our support team will assist you!",
            color=0xff6b6b  # Red color
        )
        embed.add_field(
            name="📂 Categories:",
            value="🔧 **Technical** - Installations, Troubleshooting\n📝 **Registration** - Applications, Forms, Permissions\nℹ️ **General** - Events, Resources, Rules",
            inline=False
        )
        embed.set_footer(text="Click a button below to create a support ticket")

        view = CategoryView(self.bot)

        await message.reply(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(SupportTickets(bot))