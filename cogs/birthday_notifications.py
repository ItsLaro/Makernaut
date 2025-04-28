import discord
from discord.ext import commands, tasks
from airtable import Airtable
from datetime import datetime
import os
import config

class BirthdayNotifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize Airtable connection
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        self.base_key = 'appXXXXXXXXXXXXXX'  # Replace with your Form base ID
        self.table_name = 'Student Membership Application'
        self.airtable = Airtable(self.base_key, self.table_name, self.api_key)
        
        # Channel ID for birthday announcements
        self.BIRTHDAY_CHANNEL_ID = 245393533391863808 if config.isProd else 1065042153836912714
        
        # Month name to number mapping
        self.MONTH_MAP = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        # Start the birthday check loop
        self.birthday_check.start()

    def normalize_date(self, date_str):
        """
        Normalizes different date formats to datetime object
        Handles formats:
        - mm-dd-yyyy
        - Month DD, YYYY
        """
        try:
            # Try mm-dd-yyyy format first
            if isinstance(date_str, str) and '-' in date_str:
                return datetime.strptime(date_str, '%m-%d-%Y')
            
            # Try Month DD, YYYY format
            if isinstance(date_str, str) and ',' in date_str:
                # Convert "October 25, 1999" to datetime
                month, rest = date_str.split(' ', 1)
                day, year = rest.replace(',', '').split(' ')
                month_num = self.MONTH_MAP[month.lower()]
                return datetime(int(year), month_num, int(day))
            
            # If it's already a datetime object
            if isinstance(date_str, datetime):
                return date_str
            
            raise ValueError(f"Unsupported date format: {date_str}")
            
        except Exception as e:
            print(f"Error normalizing date '{date_str}': {str(e)}")
            return None

    @tasks.loop(time=datetime.time(hour=9))  # Check at 9 AM every day
    async def birthday_check(self):
        try:
            # Get current date (month and day)
            today = datetime.now()
            current_month = today.month
            current_day = today.day

            # Fetch all records from Airtable
            records = self.airtable.get_all()
            
            for record in records:
                fields = record['fields']
                if 'Birthday' in fields:  # Note: Using 'Birthday' as the column name
                    birth_date = self.normalize_date(fields['Birthday'])
                    
                    if birth_date is None:
                        continue
                    
                    # Check if it's their birthday
                    if birth_date.month == current_month and birth_date.day == current_day:
                        channel = self.bot.get_channel(self.BIRTHDAY_CHANNEL_ID)
                        
                        if channel:
                            # Create birthday message embed
                            embed = discord.Embed(
                                title="🎉 Happy Birthday! 🎂",
                                color=discord.Color.brand_green()
                            )
                            
                            member_name = fields.get('Full Name', 'Someone')
                            discord_username = fields.get('Discord Username')
                            
                            if discord_username:
                                # Remove any @ symbol if present
                                discord_username = discord_username.lstrip('@')
                                embed.description = f"Today is {discord_username}'s birthday! 🎈\nLet's all wish them a wonderful day! 🎊"
                            else:
                                embed.description = f"Today is {member_name}'s birthday! 🎈\nLet's all wish them a wonderful day! 🎊"
                            
                            await channel.send(embed=embed)
        except Exception as e:
            print(f"Error in birthday check: {str(e)}")

    @birthday_check.before_loop
    async def before_birthday_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BirthdayNotifications(bot)) 