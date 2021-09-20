import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from pyairtable import Table
from pyairtable.formulas import match
from collections.abc import Sequence

load_dotenv()
airtable_api_key = os.environ["AIRTABLE_API_KEY"]
shellhacks_base_id = os.environ["SHELLHACKS_BASE_ID"]

class ShellHacks(commands.Cog):

    '''
    Commands specifically designed to tackle logistical needs for UPE Shellhacks
    '''

    def __init__(self, bot):
        self.bot = bot

        #Roles/Identities
        self.MODERATOR_ROLE_ID = 399551100799418370 
        self.ORGANIZER_ROLE_ID = 762734503294664706 
        self.GUI_USER_ID = 675403234172731393
        self.HACKER_ROLE_NAME = "ShellHacks Hacker"

        #Channels
        self.CHECKING_MESSAGE_ID = 889331203788914781
        self.CHECKIN_CHANNEL_ID = 888987697442590740
        self.MENTOR_CHANNEL_ID = 888969040641540146
        self.TEMPLATE_CHANNEL_ID = 888979710435029022
        self.BOT_LOGS_CHANNEL_ID = 626541886533795850
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)

        #Airtable
        self.database = Table(airtable_api_key, shellhacks_base_id, '2021 Application')

        #Colors HEX
        self.GREEN_HEX = 0x238823 
        self.RED_HEX = 0xD2222D

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.CHECKING_MESSAGE_ID:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            result = None

            initial_message = 'Please provide me with the email address you used in your application.'
            send_initial_message = await member.send(initial_message)
            
            while result == None:
                message_response = await self.bot.wait_for('message', check=message_check(channel=member.dm_channel))
                email = message_response.content

                by_email = match({"E-mail Address": email})
                result = self.database.first(formula=by_email)

                if result != None:
                    hacker_record = result["fields"]

                    try:
                        is_accepted = hacker_record['Acceptance Status'] == 'Accepted'
                    except KeyError:
                        is_accepted = False
                    try:
                        is_confirmed = hacker_record['Confirmed']
                    except KeyError:
                        is_confirmed = False
                    try:
                        is_checkedin = hacker_record['Checked In']
                    except:
                        is_checkedin = False

                    if is_accepted and is_confirmed and not is_checkedin:
                        initial_reply = "Thank you, I've verified your confirmed application!\nOne more step to help us verify your identity. Please provide your Hacker ID.\nYou can find this ID in your acceptance email and looks like this: `rec##############`\nhttps://i.imgur.com/j2z933x.png"
                        send_initial_reply = await member.send(initial_reply)

                        result = None

                        while result == None:
                            message_response = await self.bot.wait_for('message', check=message_check(channel=member.dm_channel))
                            record_id = message_response.content
                            by_email_and_id = match({"Application ID": record_id, "E-mail Address": email})
                            result = self.database.first(formula=by_email_and_id)
                            
                            if result != None:
                                hacker_role = discord.utils.get(guild.roles, name=self.HACKER_ROLE_NAME)
                                await member.add_roles(hacker_role) 

                                self.database.update(record_id, {"Checked In": True, "Discord": str(member)})
                                
                                final_reply = "You're all set! Happy Hacking~! <:upeshellhacks:753692446621433927>"
                                send_final_reply = await member.send(final_reply)

                                await self.log_channel.send(f'<:upeshellhacks:753692446621433927> {member.mention} has **checked-in** to ShellHacks 2021!')

                            else:
                                final_reply = "I couldn't verify your identity. Make sure the ID is correct and try again. (Tip: try copy/pasting it)"
                                send_final_reply = await member.send(final_reply)

                    elif is_accepted and not is_confirmed:
                        initial_reply = "Thank you! Please try again after you confirm your acceptance.\n You can try again by unreacting and reacting again in the #check-in channel"
                        send_initial_reply = await member.send(initial_reply)
                    elif is_checkedin:
                        initial_reply = "It seems you've already checked in! If you believe this is a mistake, please contact an organizer."
                        send_initial_reply = await member.send(initial_reply)                        
                    else:
                        initial_reply = "It seems like your application is still pending. If you believe this is a mistake, please contact an organizer."
                        send_initial_reply = await member.send(initial_reply)

                else:
                    initial_reply = "I wasn't able to find a matching email address. Make sure to provide the same one you used in your application."
                    send_initial_reply = await member.send(initial_reply)
    
    @commands.Cog.listener()
    async def on_message(self, payload):
        if payload.channel.id == self.MENTOR_CHANNEL_ID or payload.channel.id == self.CHECKIN_CHANNEL_ID:
            if payload.author.id == self.bot.user.id or payload.author.id == self.GUI_USER_ID:
                return
            else:
                await payload.delete()

    @commands.command()    
    async def ticket(self, ctx):
        create_ticket_channel = self.bot.get_channel(self.MENTOR_CHANNEL_ID)
        if ctx.channel != create_ticket_channel:
            return
        guild = ctx.guild
        template_channel = guild.get_channel(self.TEMPLATE_CHANNEL_ID)
        name = ctx.author.name.replace(' ', '-')
        ticket_channel = await template_channel.clone(name='📑│ticket-' + name)
        await ticket_channel.set_permissions(target=ctx.author, read_messages=True, send_messages=True, read_message_history=True)
        await ticket_channel.send(ctx.author.mention + ' you can ask the mentors questions in this channel, please close it using `?close` here when you\'re satisfied with the help you\'ve received.')
        await ctx.message.delete()

    @commands.command()    
    async def close(self, ctx):
        if 'ticket' in ctx.channel.name and ctx.channel.id != self.MENTOR_CHANNEL_ID and ctx.channel.id != self.TEMPLATE_CHANNEL_ID:
            await ctx.channel.delete()
            print("Channel closed.")
        else:
            await ctx.send("Sorry, this command only works for ticket channels")

    @commands.command()    
    async def gethacker(self, ctx, hacker_email):
        '''
        Used to fetch a hacker record based on email address from Shell DB.\nEx: ?gethacker roary@fiu.edu
        '''
        author_roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)
        organizer_role = ctx.guild.get_role(self.ORGANIZER_ROLE_ID)
        response_title = None
        response_description = f"<a:utilfailure:809713365088993291> Hacker record could not be found..."
        embed_color = self.RED_HEX
        success = False

        if (mod_role not in author_roles) and (organizer_role not in author_roles):
            response_description += f'{ctx.author.mention} this command is only meant to be used by Moderators or Shell Directors'
        else:
            by_email = match({"E-mail Address": hacker_email})
            response = self.database.first(formula=by_email)
            if(response != None):
                success = True
                hacker_record = response["fields"]
                response_description = f"ID: {hacker_record['Application ID']}"
                response_title = "Hacker Record <a:verified:798786443903631360>"
                embed_color = self.GREEN_HEX

        embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
        if success:
            embed_response.add_field(name=f"Name", value=hacker_record['First Name'] + " " + hacker_record['Last Name'], inline=False)
            embed_response.add_field(name=f"Email", value=hacker_record['E-mail Address'], inline=False)
            embed_response.add_field(name=f"Country", value=hacker_record['Country'], inline=False)
            embed_response.add_field(name=f"Status", value=hacker_record['Acceptance Status'], inline=False)
            try:
                embed_response.add_field(name=f"Confirmed", value=hacker_record['Confirmed'], inline=False)
            except KeyError:
                embed_response.add_field(name=f"Confirmed", value=False, inline=False)
            try:
                embed_response.add_field(name=f"Checked In", value=hacker_record['Checked In'], inline=False)
            except KeyError:
                embed_response.add_field(name=f"Checked In", value=False, inline=False)
            
        await ctx.send(embed=embed_response)


# auxiliary function for the message_check function to make a string sequence of the given parameter
def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)

# function to make logical checks when receiving DMs
def message_check(channel=None, author=None, content=None, ignore_bot=True, lower=True):
    channel = make_sequence(channel)
    author = make_sequence(author)
    content = make_sequence(content)
    if lower:
        content = tuple(c.lower() for c in content)
    # check that the sender of DM is the same as the receiver of the original DM from bot
    def check(message):
        if ignore_bot and message.author.bot:
            return False
        if channel and message.channel not in channel:
            return False
        if author and message.author not in author:
            return False
        actual_content = message.content.lower() if lower else message.content
        if content and actual_content not in content:
            return False
        return True
    return check

def setup(bot):
    bot.add_cog(ShellHacks(bot)) 