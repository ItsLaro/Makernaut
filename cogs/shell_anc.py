import discord
from discord.ext import commands, tasks
from helpers.notion import NotionDB
import asyncio
from datetime import datetime
import pytz

class ShellAnnouncements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notion_db = NotionDB()
        self.preview_channel_id = 1418734017322418216  # channel for previews
        self.announcement_channel_id = 1420250410308079648  # channel for actual announcements
        self.announcement_data = {}
        print(f"ShellAnnouncements cog loaded!")
        print(f"Preview Channel ID: {self.preview_channel_id}")
        print(f"Announcement Channel ID: {self.announcement_channel_id}")
    
    @tasks.loop(minutes=7)
    async def check_pending_announcements_task(self):
        await self.process_pending_announcements()
    
    async def process_pending_announcements(self):
        print("Checking for pending announcements...")
        try:
            # get pending announcements from notion
            pending_announcements = self.notion_db.get_pending_announcements()
            print(f"Found {len(pending_announcements)} pending announcements")
            
            preview_channel = self.bot.get_channel(self.preview_channel_id)
            
            if not preview_channel:
                print(f"Preview channel {self.preview_channel_id} not found")
                return
            
            print(f"Found preview channel: {preview_channel.name} ({preview_channel.id})")
            
            for announcement in pending_announcements:
                print("Sending announcement preview...")
                await self.send_announcement_preview(preview_channel, announcement)
                
        except Exception as e:
            print(f"Error processing announcements: {e}")
            import traceback
            traceback.print_exc()
    
    async def send_announcement_preview(self, channel, announcement):
        try:
            print("Creating announcement preview...")

            announcement_text = announcement["Announcement"]["formatted"]
            time_info = announcement["Time"]["formatted"]
            
            # shortened announcement for debug
            print(f"Announcement text: {announcement_text[:100]}...")
            print(f"Time: {time_info}")
            
            formatted_time = self.format_time_for_display(time_info)
            
            embed = discord.Embed(
                title="Announcement Preview",
                description=announcement_text,
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name=" ",
                value=" ",
                inline=False
            )

            embed.add_field(
                name="⏰ Scheduled Time",
                value=formatted_time,
                inline=False
            )
                        
            embed.set_footer(text="React with ✅ to send or ❌ to cancel")
            
            print("Sending embed to Discord...")
            message = await channel.send(embed=embed)
            print(f"Embed sent successfully! Message ID: {message.id}")
            
            self.announcement_data[message.id] = announcement
            
            print("Adding reaction emojis...")
            await message.add_reaction("✅")
            await message.add_reaction("❌")
            print("Reactions added successfully!")
            
        except Exception as e:
            print(f"Error sending announcement preview: {e}")
            import traceback
            traceback.print_exc()
    
    def format_time_for_display(self, time_str):
        try:
                        
            if 'T' in time_str:
                dt_str = time_str.split('T')[0] + ' ' + time_str.split('T')[1].split('.')[0]
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                
                edt = pytz.timezone('US/Eastern')
                dt_edt = edt.localize(dt)
                
                # formats time (ex: 9:20PM EDT)
                return dt_edt.strftime('%I:%M%p EDT')
            else:
                return time_str  # return original time format unparsable
                
        except Exception as e:
            print(f"Error formatting time: {e}")
            return time_str
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        # ignore bot reactions (self reactions)
        if user.bot:
            return
        
        # handle reactions on messages from this bot
        if reaction.message.author != self.bot.user:
            return
        
        # ignore reactions on other bot messages
        if not reaction.message.embeds or not reaction.message.embeds[0].title == "Announcement Preview":
            return
        
        try:
            if reaction.emoji == "✅":
                await self.send_actual_announcement(reaction.message)
                
            elif reaction.emoji == "❌":
                await reaction.message.delete()
                
                if reaction.message.id in self.announcement_data:
                    del self.announcement_data[reaction.message.id]
                
        except Exception as e:
            print(f"Error handling reaction: {e}")
    
    async def send_actual_announcement(self, preview_message):
        try:

            embed = preview_message.embeds[0]
            announcement_text = embed.description
            
            announcement_channel = self.bot.get_channel(self.announcement_channel_id)
            if not announcement_channel:
                print(f"Announcement channel {self.announcement_channel_id} not found")
                return
            
            await announcement_channel.send(announcement_text)
            
            announcement_data = self.announcement_data.get(preview_message.id)
            if announcement_data:
                success = self.notion_db.mark_announcement_sent(announcement_data)
                if success:
                    print("Announcement marked as 'Done' in Notion database")
                else:
                    print("Failed to update Notion database")

                del self.announcement_data[preview_message.id]
            else:
                print("No announcement data found for this message")
            
            await preview_message.delete()
            
        except Exception as e:
            print(f"Error sending actual announcement: {e}")
    
    def cog_load(self):

        print("Starting announcement check task...")
        self.check_pending_announcements_task.start()
        print("Announcement check task started!")
    
    @check_pending_announcements_task.before_loop
    async def before_check_pending_announcements_task(self):
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        self.check_pending_announcements_task.cancel()

async def setup(bot):
    await bot.add_cog(ShellAnnouncements(bot))
