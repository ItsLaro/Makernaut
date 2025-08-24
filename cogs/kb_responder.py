import discord
from discord.ext import commands
import config

class KBResponder(commands.Cog):
    """
    Main message handler that coordinates KB search and support tickets
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.UPE_GUILD_ID = 245393533391863808 if config.isProd else 1065042153836912714
    
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
                print(kb_result)
                return
            print("No KB result found.")

        # No KB answer found - show support ticket options
        support_tickets = self.bot.get_cog('SupportTickets')
        if support_tickets:
            await support_tickets.show_category_buttons(message)

async def setup(bot):
    await bot.add_cog(KBResponder(bot))