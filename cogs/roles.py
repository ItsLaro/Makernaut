import discord
from discord.ext import commands
from discord import app_commands

class Roles(commands.Cog):

    '''
    Handles role-related commands and events. Allows  assignment of other other roles via reactions.
    Handles commands to manually manipulate roles.
    '''
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370  #Current: Main; Test: 788930867593871381
        self.WHISPERER_ROLE_ID = 797617839355854848 #Additional role for Eboard and Committee members to manage certain commands.

        #Channels
        self.BOT_LOGS_CHANNEL_ID = 626541886533795850
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)

        #Messages
        self.ROLE_EVENT_ASSIGNMENT_MESSAGE_ID = 804525065420668958 ##CHANGE THIS FOR EVENTS. (like Global Game Jam, PantherHacks and ShellHacks!)
        self.ROLE_UPE_ASSIGNMENT_MESSAGE_ID = 798334433957773343
        self.ROLE_SOCIAL_ASSIGNMENT_MESSAGE_ID = 798334792349384714
        
        #Roles
        # self.EVENT_NAME = "Global Game Jam 2021"
        # self.EVENT_ROLE_NAME = "GGJ Jammer" #CHANGE THIS FOR EVENTS.

        # self.CODE_ROLE_NAME = "Code"
        # self.MAKE_ROLE_NAME = "Make"
        # self.INFOTECH_ROLE_NAME = "InfoTech"
        # self.DESIGN_ROLE_NAME = "Design"
        # self.LEAP_ROLE_NAME = "Leap"
        # self.IGNITE_ROLE_NAME = "Ignite"
        # self.SPARKDEV_ROLE_NAME = "SparkDev"
        # self.SHELLHACKS_ROLE_NAME = "ShellHacks"
        # self.DISCOVER_ROLE_NAME = "Discover"

        # self.OPPORTUNITY_ROLE_NAME = "Opportunity Seekers"
        # self.WOMENINTECH_ROLE_NAME = "Women In Tech"
        # self.FITNESSCREW_ROLE_NAME = "Fitness Crew"
        # self.AMONGUS_ROLE_NAME = "Among Us"
        # self.GACHA_ROLE_NAME = "Tamagotchi Tamers"
        # self.POKE_ROLE_NAME = "Pokemon Trainers"
        # self.TAMAGOTCHI_ROLE_NAME = "Gacha Addicts"
        # self.ANIME_ROLE_NAME = "Anime Bingers"

        # #Emojis
        # self.emoji_event = '<:GGJ21:804515872449232896>'
        # self.emojis_upe = {
        #     self.CODE_ROLE_NAME : "<:upecode:753692446738612384>",
        #     self.MAKE_ROLE_NAME : "<:upemake:753692447044927518>",
        #     self.INFOTECH_ROLE_NAME :"<:upeinfotech:753692446726029388>",
        #     self.DESIGN_ROLE_NAME : "<:upedesign:797531069951770674>",
        #     self.LEAP_ROLE_NAME : "<:upeleap:882407121923227648>",
        #     self.IGNITE_ROLE_NAME : "<:upeignite:753692446801789039>",
        #     self.SPARKDEV_ROLE_NAME : "<:upesparkdev:753692446784880760>",
        #     self.SHELLHACKS_ROLE_NAME : "<:upeshellhacks:753692446621433927>",
        #     self.DISCOVER_ROLE_NAME : "<:upediscover:753692446524702782>"
        # }
        # self.emojis_misc = {
        #     self.OPPORTUNITY_ROLE_NAME : "<:blobjob:797536764863578142>",
        #     self.WOMENINTECH_ROLE_NAME : "<:blobwit:797536764885073950>",
        #     self.FITNESSCREW_ROLE_NAME : "<:blobfit:797541060565401600>",
        #     self.AMONGUS_ROLE_NAME : "<:blobimposter:797536765052977152>",
        #     self.GACHA_ROLE_NAME : "<:blobtama:797536764554248214>",
        #     self.POKE_ROLE_NAME : "<:blobpoke:797536764700131338>",
        #     self.TAMAGOTCHI_ROLE_NAME : "<:bloboro:558279426086010890>",
        #     self.ANIME_ROLE_NAME : "<:blobpopcorn:797958181081841664>"
        # }

        #Colors HEX
        self.BLUE_HEX = 0x3895D3
        self.GREEN_HEX = 0x238823 
        self.YELLOW_HEX = 0xFFBF00  
        self.RED_HEX = 0xD2222D
        
    @app_commands.command(name="see_roles", description="Inquire about an existing server role")
    async def seerole(self, interaction: discord.Interaction, role_name: str):

        '''
        Used to acquire information about a role.\nEx: ?seerole Code Member
        '''
        is_success = False
        response_title = None
        response_description = f"<a:utilfailure:809713365088993291> "
        response_users = "N/A"
        embed_color = self.RED_HEX

        roles = interaction.user.roles
        mod_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = interaction.guild.get_role(self.WHISPERER_ROLE_ID)

        role_members = []
        role_members_count = 0
        
        if (mod_role not in roles) and (whisperer_role not in roles):
            response_description += f'{interaction.author.mention} this command is only meant to be used by Moderators or Program Organizers'
        else:
            desired_role = None
            if len(role_name) == 0:
                response_description += "You must include the name of the role to see"
            else:
                desired_role = discord.utils.get(interaction.guild.roles, name=role_name)

                if not desired_role:
                    response_description += f'Role "{role_name}"could not be found... Verify and try again!'
                else:
                    for member in interaction.guild.members:
                        if desired_role in member.roles:
                            role_members.append(str(member))
                            role_members_count += 1
                    
                    role_members.append("───────")
                    is_success = True

        if is_success:
            response_title = "Role Info"
            response_description = f"**Name:** *{str(desired_role)}*\n**Position:** {desired_role.position}\n**Hoisted:** {desired_role.hoist}\n**Mentionable:** {desired_role.mentionable}\n**ID:** {desired_role.id}\n**Creation Date:** {desired_role.created_at.date()}"
            response_users = "\n".join(role_members[:15]) #TODO: Implement Pagination with Discord Reactions. 
            embed_color = desired_role.color
            
        embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
        embed_response.add_field(name=f"Users: ({role_members_count})", value=response_users, inline=False)
        await interaction.response.send_message(embed=embed_response)

    @commands.command()
    async def giverole(self, ctx, member_name=None, *args):
        '''
        Used to assign a role to a user.\nEx: ?giverole @Laro#0001 Code Member
        '''
        is_success = False
        response_description = f"<a:utilfailure:809713365088993291> "
        embed_color = self.RED_HEX

        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = ctx.guild.get_role(self.WHISPERER_ROLE_ID)

        if (mod_role not in roles) and (whisperer_role not in roles):
            response_description += f'{ctx.author.mention} this command is only meant to be used by Moderators or Program Organizers'
        else:
            desired_role = None

            try:
                target_user = await commands.MemberConverter().convert(ctx, member_name)
            except commands.BadArgument:
                response_description += f'"{member_name}" is not a valid member or member ID.\nYou must include the full tag of the user (Ex. @User#0000)'
            except commands.MemberNotFound:
                response_description += f'"{member_name}" is not a user in this server'
            else:
                if len(args) == 0:
                    response_description += "You must include the name of the role after the user"
                else:
                    desired_role_name = (" ".join(args)).strip()
                    desired_role = discord.utils.get(ctx.guild.roles, name=desired_role_name)

                    if not desired_role:
                        response_description += f'Role "{desired_role_name}"could not be found... Verify and try again!'
                    else:
                        await target_user.add_roles(desired_role)
                        is_success = True

        if is_success:
            response_description = f"<a:verified:798786443903631360> Added Role: + {str(desired_role)} to {target_user.mention}"
            embed_color = self.GREEN_HEX
            
        embed_response = discord.Embed(title=None, description=response_description, color=embed_color)
        await ctx.send(embed=embed_response)
    
    @commands.command()
    async def takerole(self, ctx, member_name, *args):

        '''
        Used to remove a role to a user.\nEx: ?takerole @Laro#0001 InfoTech Member
        '''
        is_success = False
        response_description = f"<a:utilfailure:809713365088993291> "
        embed_color = self.RED_HEX

        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = ctx.guild.get_role(self.WHISPERER_ROLE_ID)

        if (mod_role not in roles) and (whisperer_role not in roles):
            response_description += f'{ctx.author.mention} this command is only meant to be used by Moderators or Program Organizers'
      
        else:
            desired_role = None

            try:
                target_user = await commands.MemberConverter().convert(ctx, member_name)
            except commands.BadArgument:
                response_description += f'"{member_name}" is not a valid member or member ID.\nYou must include the full tag of the user (Ex. @User#0000)'
            except commands.MemberNotFound:
                response_description += f'"{member_name}" is not a user in this server'
            else:

                if len(args) == 0:
                    response_description += "You must include the name of the role after the user"
                else:
                    desired_role_name = (" ".join(args)).strip()
                    desired_role = discord.utils.get(ctx.guild.roles, name=desired_role_name)

                    if not desired_role:
                        response_description += f'Role "{desired_role_name}"could not be found... Verify and try again!'
                    else:
                        
                        if desired_role not in target_user.roles:
                            response_description += f"User {target_user} did not have the {desired_role} role."
                        else:
                            await target_user.remove_roles(desired_role)
                            is_success = True

        if is_success:
            response_description = f"<a:verified:798786443903631360> Removed Role: - {str(desired_role)} from {target_user.mention}"
            embed_color = self.GREEN_HEX
            
        embed_response = discord.Embed(title=None, description=response_description, color=embed_color)
        await ctx.send(embed=embed_response)

    @commands.command()
    async def purgerole(self, ctx, *args):

        '''
        Removes the specified role from ALL users.\nEx: ?purgerole SparkDev Member
        '''
        
        is_success = False
        response_description = f"<a:utilfailure:809713365088993291> "
        embed_color = self.RED_HEX

        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)

        if mod_role not in roles:
            response_description += f'{ctx.author.mention} this command is only meant to be used by Moderators'
        else:
            old_role = None

            if not args:
                response_description += "You must include the name of the role to be purged"
            else:
                role_name = " ".join(args)
                old_role = discord.utils.get(ctx.guild.roles, name=role_name)

                if not old_role:
                    response_description += f"Role {role_name} couldn't not be found... Verify and try again!"
                else:
                    response_description = f"Attempting to purge the {old_role} from all members..."
                    embed_response = discord.Embed(title="<a:utilloading:809712534961389649> In Progress...", description=response_description, color=self.YELLOW_HEX)
                    response = await ctx.send(embed=embed_response)

                    for member in ctx.guild.members:
                        if old_role in member.roles:
                            await member.remove_roles(old_role)

                    is_success = True
        
        if is_success:
            response_description = f"<a:verified:798786443903631360> Purged Role: :toilet: {str(old_role)} from **All Users**"
            embed_color = self.GREEN_HEX
            embed_response = discord.Embed(title=None, description=response_description, color=embed_color)
            await response.edit(embed=embed_response)
        else:   
            embed_response = discord.Embed(title=None, description=response_description, color=embed_color)
            await ctx.send(embed=embed_response)

    @commands.command()
    async def massgiverole(self, ctx, *args):

        '''
        Used to add the same role to multiple users.\nEx: ?massgiverole Design Member | @Laro#0001 @JohnDoe#1234 @Mudae#0807
        '''
        is_success = False
        response_title = None
        response_description = f"<a:utilfailure:809713365088993291> "
        has_succesful_users = False
        has_failed_users = False
        embed_color = self.RED_HEX

        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = ctx.guild.get_role(self.WHISPERER_ROLE_ID)

        role_name_words = []
        is_mention_argument = False
        num_role_args = 0

        word_count = len(" ".join(args))
        if (mod_role not in roles) and (whisperer_role not in roles):
            response_description += f'{ctx.author.mention} this command is only meant to be used by Moderators and Program Organizers.'
        elif  word_count > 800:
            response_description += f'{ctx.author.mention}, your request surpassed the word limit: {word_count}/800.'
        else:
            role = None

            if len(args) < 3:
                response_description += "You must include the name of the role and mention all the users"
            else:
                for arg in args:
                    if is_mention_argument:
                        pass
                    else:
                        if arg != '|':
                            role_name_words.append(arg)
                        else:
                            is_mention_argument = True #indicates the next args are users
                        num_role_args += 1

                role_name = " ".join(role_name_words)
                role = discord.utils.get(ctx.guild.roles, name=role_name)

                if not role:
                    response_description += "Role couldn't not be found... Verify and try again!\nMake sure you're using `|` between the role and the users"
                else:
                    response_description = f"Attempting to assign the {str(role)} role to multiple users"
                    embed_response = discord.Embed(title="<a:utilloading:809712534961389649> In Progress...", description=response_description, color=self.YELLOW_HEX)
                    response = await ctx.send(embed=embed_response)

                    succesful_users = [] #List to hold the name of users who now have the role.
                    failed_users = [] #List to hold the name of users who failed to acquire the role.

                    for member_name in args[num_role_args:]:
                        try:
                            member = await commands.MemberConverter().convert(ctx, member_name)
                        except commands.BadArgument:
                            failed_users.append(member_name)
                        except commands.MemberNotFound:
                            failed_users.append(member_name)
                        else:
                            await member.add_roles(role)
                            succesful_users.append(member.mention)

                    is_success = True

                    #Final Response 
                    response_description = f"Added Role: +{str(role)}"
                    response_succesful_users = ", ".join(succesful_users)
                    response_failed_users = ", ".join(failed_users)
                    has_failed_users = bool(failed_users)
                    has_succesful_users = bool(succesful_users)
                    
                    if not has_failed_users:
                        response_title = "<a:verified:798786443903631360> Done!"
                        embed_color = self.GREEN_HEX
                    elif has_succesful_users:
                        response_title = "<a:verified:798786443903631360> Done. Please Review."
                        embed_color = self.YELLOW_HEX 
                    else:
                        response_title = "<a:utilfailure:809713365088993291> Failed..."
                        embed_color = self.RED_HEX

        if is_success:
            embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
            if has_succesful_users:
                embed_response.add_field(name="Succesful on:", value=response_succesful_users, inline=False)
            if has_failed_users:
                embed_response.add_field(name="Failed on:", value=response_failed_users, inline=False)
            await response.edit(embed=embed_response)
        else:
            embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
            await ctx.send(embed=embed_response)

    @commands.command()
    async def replacerole(self, ctx, *args):
        '''
        Used to replace a role for another on every user.\nEx: ?replacerole ShellHacks Hacker | ShellHacks 2018 Hacker
        '''
        is_success = False
        response_title = None
        response_description = f"<a:utilfailure:809713365088993291> "
        embed_color = self.RED_HEX
        
        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)

        if mod_role not in roles:
                response_description += f'{ctx.author.mention} this command is only meant to be used by Moderators.'
        else:
            old_role = None
            new_role = None

            if not args:
                response_description += "You must include the current role name,\n followed by the new role name ( Separated by a `|` )"
            else:
                roles_name = " ".join(args)
                roles_name_list = roles_name.split("|")

                if len(roles_name_list) < 2:
                    response_description += "You must include the current role name,\n followed by the new role name ( Separated by a `|` )"
                else: 
                    old_role = discord.utils.get(ctx.guild.roles, name=roles_name_list[0].strip())
                    new_role = discord.utils.get(ctx.guild.roles, name=roles_name_list[1].strip())

                    if not old_role:
                        response_description += "Current role couldn't not be found... Verify and try again!"
                    elif not new_role:
                        response_description += "New role couldn't not be found... Verify and try again!"
                    else:
                        response_description = f"Attempting to give members with the {old_role} role the {new_role} role instead..."
                        embed_response = discord.Embed(title="<a:utilloading:809712534961389649> In Progress...", description=response_description, color=self.YELLOW_HEX)
                        response = await ctx.send(embed=embed_response)

                        for member in ctx.guild.members:
                            if old_role in member.roles:
                                await member.add_roles(new_role)
                                await member.remove_roles(old_role)
                        is_success = True

        if is_success:
            response_title = "<a:verified:798786443903631360> Done!"
            response_description = f"Replaced Role: {old_role} :arrow_right: {new_role}"
            embed_color = self.GREEN_HEX
            embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
            await response.edit(embed=embed_response)
        else:
            embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
            await ctx.send(embed=embed_response)

async def setup(bot):
    await bot.add_cog(Roles(bot), guilds=[discord.Object(id=245393533391863808)]) 