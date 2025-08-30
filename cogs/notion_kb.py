import discord
import os
import time
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
        self.cache = {"data": [], "timestamp": 0}
        self.UPE_GUILD_ID = config.UPE_GUILD_ID

    async def _update_cache(self):
        """Queries Notion and updates the local cache."""
        print("Updating Notion KB cache...")
        results = self.notion.databases.query(database_id=self.database_id)
        self.cache["data"] = results.get("results", [])
        self.cache["timestamp"] = time.time()
        print("Cache updated successfully.")
        
    async def search_kb(self, question):
        """Search the Notion KB for an answer to the question"""
        try:
            # Query the Notion database
            if time.time() - self.cache["timestamp"] > 300:
                await self._update_cache()
            
            best_match = None
            best_score = 0
            
            # Search through the needed entries
            for page in self.cache["data"]:
                properties = page.get("properties", {})
                
                # MODIFIED: Safer data extraction using .get()
                title_list = properties.get("Question", {}).get("title", [])
                answer_list = properties.get("Answer", {}).get("rich_text", [])
                category_obj = properties.get("Category", {}).get("select", {})

                kb_question = title_list[0].get("text", {}).get("content", "") if title_list else ""
                kb_answer = answer_list[0].get("text", {}).get("content", "") if answer_list else ""
                kb_category = category_obj.get("name", "General") if category_obj else "General"

                if not kb_question:
                    continue
                
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
            title=match_data["question"],
            description=match_data["answer"],
            color=0x00ff00
        )
        
        return embed

async def setup(bot):
    await bot.add_cog(NotionKB(bot))