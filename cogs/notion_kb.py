import discord
import os
from discord.ext import commands
from notion_client import Client
from fuzzywuzzy import fuzz
import config

class NotionKB(commands.Cog):
    """
    Handles connection to Notion Knowledge Base and searching for answers
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.notion = Client(auth=config.NOTION_TOKEN)
        self.database_id = config.NOTION_KB_DATABASE_ID
        self.cache = {}  # Simple cache for responses
        self.UPE_GUILD_ID = config.UPE_GUILD_ID
        
    async def search_kb(self, question):
        """Search the Notion KB for an answer to the question"""
        try:
            # Query the Notion database
            results = self.notion.databases.query(
                database_id=self.database_id
            )
            
            best_match = None
            best_score = 0
            
            # Search through all entries
            for page in results["results"]:
                properties = page["properties"]
                
                # Get the question and answer from the database
                kb_question = ""
                kb_answer = ""
                kb_category = ""
                
                if "Question" in properties:
                    kb_question = properties["Question"]["title"][0]["text"]["content"] if properties["Question"]["title"] else ""
                
                if "Answer" in properties:
                    kb_answer = properties["Answer"]["rich_text"][0]["text"]["content"] if properties["Answer"]["rich_text"] else ""
                
                if "Category" in properties:
                    kb_category = properties["Category"]["select"]["name"] if properties["Category"]["select"] else ""
                
                # Use fuzzy matching to find similar questions
                similarity = fuzz.ratio(question.lower(), kb_question.lower())
                
                if similarity > best_score and similarity > 60:  # 60% similarity threshold
                    best_score = similarity
                    best_match = {
                        "question": kb_question,
                        "answer": kb_answer,
                        "category": kb_category,
                        "similarity": similarity
                    }
            
            return best_match
            
        except Exception as e:
            print(f"Error searching Notion KB: {e}")
            return None
    
    def format_kb_response(self, match_data):
        """Format the KB response into a Discord embed"""
        embed = discord.Embed(
            title="📚 Knowledge Base",
            description=match_data["answer"],
            color=0x00ff00  # Green color
        )
        embed.add_field(name="Question", value=match_data["question"], inline=False)
        embed.add_field(name="Category", value=match_data["category"], inline=True)
        embed.add_field(name="Confidence", value=f"{match_data['similarity']}%", inline=True)
        embed.set_footer(text="Powered by Notion KB")
        
        return embed

async def setup(bot):
    await bot.add_cog(NotionKB(bot))