import discord
from discord.ext import commands
from discord import app_commands
import config

class Voice(commands.Cog):

    temporary_channels = []

    def __init__(self, bot):
        self.bot = bot
        self.room_creation_vc_id = 1069364875391930478 if config.isProd else 1069365536120643705

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        possible_channel_name = f"{member.display_name}'s Room"
        if after.channel:
            if after.channel.id == self.room_creation_vc_id:
                temp_channel = await after.channel.clone(name=possible_channel_name)
                await member.move_to(temp_channel)
                self.temporary_channels.append(temp_channel.id)
                await temp_channel.send(f"Hey {member.mention}, welcome to your very own voice channel! If you leave the channel and its contents will be deleted.")
        if before.channel:
            if before.channel.id in self.temporary_channels:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
        

async def setup(bot):
    await bot.add_cog(Voice(bot))