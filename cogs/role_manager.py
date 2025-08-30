import discord
import time
from discord.ext import commands
from notion_client import Client
import config

class RoleManager(commands.Cog):
    """
    Manages fetching and caching support roles from a Notion database.
    """
    def __init__(self, bot):
        self.bot = bot
        self.notion = Client(auth=config.NOTION_TOKEN)
        self.database_id = config.NOTION_SUPPORT_DATABASE_ID
        self.role_cache = {"data": {}, "timestamp": 0}

    @commands.Cog.listener()
    async def on_ready(self):
        """Update cache on bot startup."""
        await self._update_role_cache()

    async def _update_role_cache(self):
        """Queries Notion for support roles and updates the local cache."""
        if not self.database_id:
            print("Warning: NOTION_SUPPORT_DATABASE_ID is not set. Cannot fetch support roles.")
            return

        print("Updating Support Role cache from Notion...")
        try:
            results = self.notion.databases.query(database_id=self.database_id)
            
            new_cache = {}
            for page in results.get("results", []):
                properties = page.get("properties", {})
                
                # Extract data safely
                name_list = properties.get("Name", {}).get("title", [])
                role_id_obj = properties.get("Discord Role ID", {}).get("rich_text", [])
                categories_list = properties.get("Category", {}).get("multi_select", [])

                if not role_id_obj or not categories_list:
                    continue

                role_id_str = role_id_obj[0].get("text", {}).get("content")
                try:
                    # Ensure it's a valid integer ID
                    role_id = int(role_id_str)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid Role ID found: {role_id_str}. Skipping.")
                    continue

                for category in categories_list:
                    category_name = category.get("name")
                    if category_name:
                        if category_name not in new_cache:
                            new_cache[category_name] = []
                        new_cache[category_name].append(role_id)
            
            self.role_cache["data"] = new_cache
            self.role_cache["timestamp"] = time.time()
            print("Support Role cache updated successfully.")
            print(f"Loaded roles: {self.role_cache['data']}")

        except Exception as e:
            print(f"Error updating support role cache: {e}")

    async def get_roles_for_category(self, category_name: str) -> list[int]:
        """
        Gets the list of role IDs for a given support category.
        Refreshes cache if it's older than 5 minutes.
        """
        # Refresh cache if stale (5 minutes)
        if time.time() - self.role_cache["timestamp"] > 300:
            await self._update_role_cache()
        
        # Return the list of role IDs for the category, or an empty list if not found
        return self.role_cache["data"].get(category_name, [])

async def setup(bot):
    await bot.add_cog(RoleManager(bot))
