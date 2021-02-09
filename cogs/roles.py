import discord
from discord.ext import commands

class Roles(commands.Cog):

    '''
    Handles role-related commands and events. Allows user verification by reactions and assignment of other other roles via reactions.
    Handles commnds to manually give or substitute roles.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 788930867593871381 #Current: Test; Main: 399551100799418370
        self.WHISPERER_ROLE_ID = 797617839355854848 #Additional role for Eboard and Committee members to manage certain commands.

        #Channels
        self.BOT_LOGS_CHANNEL_ID = 626541886533795850
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)

        #Messages
        self.ROLE_EVENT_ASSIGNMENT_MESSAGE_ID = 804525065420668958 ##CHANGE THIS FOR EVENTS. (like Global Game Jam, PantherHacks and ShellHacks!)
        self.ROLE_UPE_ASSIGNMENT_MESSAGE_ID = 798334433957773343
        self.ROLE_SOCIAL_ASSIGNMENT_MESSAGE_ID = 798334792349384714
        
        #Roles
        self.EVENT_NAME = "Global Game Jam 2021"
        self.EVENT_ROLE_NAME = "GGJ Jammer" #CHANGE THIS FOR EVENTS.

        self.CODE_ROLE_NAME = "Code"
        self.MAKE_ROLE_NAME = "Make"
        self.INFOTECH_ROLE_NAME = "InfoTech"
        self.DESIGN_ROLE_NAME = "Design"
        self.ADVANCE_ROLE_NAME = "Advance"
        self.IGNITE_ROLE_NAME = "Ignite"
        self.SPARKDEV_ROLE_NAME = "SparkDev"
        self.MENTOR_ROLE_NAME = "Mentor"
        self.SHELLHACKS_ROLE_NAME = "ShellHacks"
        self.DISCOVER_ROLE_NAME = "Discover"

        self.OPPORTUNITY_ROLE_NAME = "Opportunity Seekers"
        self.WOMENINTECH_ROLE_NAME = "Women In Tech"
        self.FITNESSCREW_ROLE_NAME = "Fitness Crew"
        self.AMONGUS_ROLE_NAME = "Among Us"
        self.GACHA_ROLE_NAME = "Tamagotchi Tamers"
        self.POKE_ROLE_NAME = "Pokemon Trainers"
        self.TAMAGOTCHI_ROLE_NAME = "Gacha Addicts"

        #Emojis
        self.emoji_event = '<:GGJ21:804515872449232896>'
        self.emojis_upe = {
            self.CODE_ROLE_NAME : "<:upecode:753692446738612384>",
            self.MAKE_ROLE_NAME : "<:upemake:753692447044927518>",
            self.INFOTECH_ROLE_NAME :"<:upeinfotech:753692446726029388>",
            self.DESIGN_ROLE_NAME : "<:upedesign:797531069951770674>",
            self.ADVANCE_ROLE_NAME : "<:upeadvance:753692446776361126>",
            self.IGNITE_ROLE_NAME : "<:upeignite:753692446801789039>",
            self.SPARKDEV_ROLE_NAME : "<:upesparkdev:753692446784880760>",
            self.MENTOR_ROLE_NAME : "<:upementor:753692446776623284>",
            self.SHELLHACKS_ROLE_NAME : "<:upeshellhacks:753692446621433927>",
            self.DISCOVER_ROLE_NAME : "<:upediscover:753692446524702782>"
        }
        self.emojis_misc = {
            self.OPPORTUNITY_ROLE_NAME : "<:blobjob:797536764863578142>",
            self.WOMENINTECH_ROLE_NAME : "<:blobwit:797536764885073950>",
            self.FITNESSCREW_ROLE_NAME : "<:blobfit:797541060565401600>",
            self.AMONGUS_ROLE_NAME : "<:blobimposter:797536765052977152>",
            self.GACHA_ROLE_NAME : "<:blobtama:797536764554248214>",
            self.POKE_ROLE_NAME : "<:blobpoke:797536764700131338>",
            self.TAMAGOTCHI_ROLE_NAME : "<:bloboro:558279426086010890>"
        }

        #Colors HEX
        self.BLUE_HEX = 0x3895D3
        self.GREEN_HEX = 0x238823 
        self.YELLOW_HEX = 0xFFBF00  
        self.RED_HEX = 0xD2222D
        
    #Events
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        reacting_user = payload.member

        ### EVENT ROLE ASSIGNMENT
    
        # User added reaction to the Event Message in #welcome
        if payload.message_id == self.ROLE_EVENT_ASSIGNMENT_MESSAGE_ID:
            
            # User reacted with the appropiate emoji
            if str(payload.emoji) == self.emoji_event:
                # Sets the verified 'User' role
                event_user_role = discord.utils.get(reacting_user.guild.roles, name=self.EVENT_ROLE_NAME)
                await reacting_user.add_roles(event_user_role) 

                #Prints to console and notifies bot-log channel
                print("User " + reacting_user.name + " has entered the event!")
                await self.log_channel.send(f'{self.emoji_event} {reacting_user.mention} is attending {self.EVENT_NAME}!')

        ### UPE ROLES ASSIGNMENT

        # User added reaction to the UPE Program Roles Message in #programs
        if payload.message_id == self.ROLE_UPE_ASSIGNMENT_MESSAGE_ID:
            
            desired_user_role = None

            #Reaction is for Code:
            if str(payload.emoji) == self.emojis_upe[self.CODE_ROLE_NAME]:
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.CODE_ROLE_NAME)
            
            #Reaction is for Make:
            elif str(payload.emoji) == self.emojis_upe[self.MAKE_ROLE_NAME]:
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.MAKE_ROLE_NAME)
            
            #Reaction is for Infotech:
            elif str(payload.emoji) == self.emojis_upe[self.INFOTECH_ROLE_NAME]:
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.INFOTECH_ROLE_NAME)

            #Reaction is for Design:
            elif str(payload.emoji) == self.emojis_upe[self.DESIGN_ROLE_NAME]:
                # Sets the verified 'Interested' role
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.DESIGN_ROLE_NAME)

            #Reaction is for Advance:
            elif str(payload.emoji) == self.emojis_upe[self.ADVANCE_ROLE_NAME]:
                # Sets the verified 'Interested' role
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.ADVANCE_ROLE_NAME)

            #Reaction is for Ignite:
            elif str(payload.emoji) == self.emojis_upe[self.IGNITE_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.IGNITE_ROLE_NAME)

            #Reaction is for Sparkdev:
            elif str(payload.emoji) == self.emojis_upe[self.SPARKDEV_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.SPARKDEV_ROLE_NAME)

            #Reaction is for Mentor:
            elif str(payload.emoji) == self.emojis_upe[self.MENTOR_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.MENTOR_ROLE_NAME)

            #Reaction is for ShellHacks:
            elif str(payload.emoji) == self.emojis_upe[self.SHELLHACKS_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.SHELLHACKS_ROLE_NAME)

            #Reaction is for Discover:
            elif str(payload.emoji) == self.emojis_upe[self.DISCOVER_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.DISCOVER_ROLE_NAME)

            #Invalid reaction (unreachable condition)
            else:
                print("Unknown Reaction Added. Verify channel permissions.")
            
            if desired_user_role is not None:
                await reacting_user.add_roles(desired_user_role) 
                #Prints to console and notifies bot-log channel
                print("User " + reacting_user.name + f" is interested in {desired_user_role}!")
                await self.log_channel.send(f'{self.emojis_upe[str(desired_user_role)]} {reacting_user.mention} is interested in {desired_user_role}!')

        ### MISC ROLES ASSIGNMENT

        # User added reaction to the UPE Misc Roles Message in #additional-roles
        if payload.message_id == self.ROLE_SOCIAL_ASSIGNMENT_MESSAGE_ID:
            
            desired_user_role = None

            print(f"{payload.emoji} vs {self.emojis_misc[self.OPPORTUNITY_ROLE_NAME]}")

            #Reaction is for Opportunity Seekers:
            if str(payload.emoji) == self.emojis_misc[self.OPPORTUNITY_ROLE_NAME]:
                print("Opportunity")
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.OPPORTUNITY_ROLE_NAME)
            
            #Reaction is for Women In Tech:
            elif str(payload.emoji) == self.emojis_misc[self.WOMENINTECH_ROLE_NAME]:
                print("WIT")
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.WOMENINTECH_ROLE_NAME)
            
            #Reaction is for Fitness Crew:
            elif str(payload.emoji) == self.emojis_misc[self.FITNESSCREW_ROLE_NAME]:
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.FITNESSCREW_ROLE_NAME)

            #Reaction is for Among Us:
            elif str(payload.emoji) == self.emojis_misc[self.AMONGUS_ROLE_NAME]:
                # Sets the verified 'Interested' role
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.AMONGUS_ROLE_NAME)

            #Reaction is for Tamagotchi Tamers:
            elif str(payload.emoji) == self.emojis_misc[self.TAMAGOTCHI_ROLE_NAME]:
                # Sets the verified 'Interested' role
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.TAMAGOTCHI_ROLE_NAME)

            #Reaction is for Pokemon Trainers:
            elif str(payload.emoji) == self.emojis_misc[self.POKE_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.POKE_ROLE_NAME)

            #Reaction is for Gacha Addicts:
            elif str(payload.emoji) == self.emojis_misc[self.GACHA_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.GACHA_ROLE_NAME)

            #Invalid reaction (unreachable condition)
            else:
                print("Unknown Reaction Added. Verify channel permissions.")
            
            if desired_user_role is not None:
                await reacting_user.add_roles(desired_user_role) 
                print("User " + reacting_user.name + f" is interested in {desired_user_role}!")

    #Events
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        
        guild = await self.bot.fetch_guild(payload.guild_id)
        reacting_user = await guild.fetch_member(payload.user_id) 
        
        ### EVENT ROLE ASSIGNMENT
    
        # User added reaction to the Rules Acceptance Message in #welcome
        if payload.message_id == self.ROLE_EVENT_ASSIGNMENT_MESSAGE_ID:

            # User reacted with the appropiate emoji
            if str(payload.emoji) == self.emoji_event:
                # Sets the verified 'User' role
                event_user_role = discord.utils.get(reacting_user.guild.roles, name=self.EVENT_ROLE_NAME)
                await reacting_user.remove_roles(event_user_role) 

                #Prints to console and notifies bot-log channel
                print("User " + reacting_user.name + " has exited the event!")                
                await self.log_channel.send(f'{self.emoji_event} {reacting_user.mention} has *left* {self.EVENT_NAME}!')


        ### UPE ROLES ASSIGNMENT

        # User added reaction to the UPE Program Roles Message in #programs
        if payload.message_id == self.ROLE_UPE_ASSIGNMENT_MESSAGE_ID:
            
            desired_user_role = None

            #Reaction is for Code:
            if str(payload.emoji) == self.emojis_upe[self.CODE_ROLE_NAME]:
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.CODE_ROLE_NAME)
            
            #Reaction is for Make:
            elif str(payload.emoji) == self.emojis_upe[self.MAKE_ROLE_NAME]:
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.MAKE_ROLE_NAME)
            
            #Reaction is for Infotech:
            elif str(payload.emoji) == self.emojis_upe[self.INFOTECH_ROLE_NAME]:
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.INFOTECH_ROLE_NAME)

            #Reaction is for Design:
            elif str(payload.emoji) == self.emojis_upe[self.DESIGN_ROLE_NAME]:
                # Sets the verified 'Interested' role
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.DESIGN_ROLE_NAME)

            #Reaction is for Advance:
            elif str(payload.emoji) == self.emojis_upe[self.ADVANCE_ROLE_NAME]:
                # Sets the verified 'Interested' role
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.ADVANCE_ROLE_NAME)

            #Reaction is for Ignite:
            elif str(payload.emoji) == self.emojis_upe[self.IGNITE_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.IGNITE_ROLE_NAME)

            #Reaction is for Sparkdev:
            elif str(payload.emoji) == self.emojis_upe[self.SPARKDEV_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.SPARKDEV_ROLE_NAME)

            #Reaction is for Mentor:
            elif str(payload.emoji) == self.emojis_upe[self.MENTOR_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.MENTOR_ROLE_NAME)

            #Reaction is for ShellHacks:
            elif str(payload.emoji) == self.emojis_upe[self.SHELLHACKS_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.SHELLHACKS_ROLE_NAME)

            #Reaction is for Discover:
            elif str(payload.emoji) == self.emojis_upe[self.DISCOVER_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.DISCOVER_ROLE_NAME)

            #Invalid reaction (unreachable condition)
            else:
                print("Unknown Reaction Added. Verify channel permissions.")
            
            if desired_user_role is not None:
                await reacting_user.remove_roles(desired_user_role) 
                #Prints to console and notifies bot-log channel
                print("User " + reacting_user.name + f" is NO longer interested in {desired_user_role}!")

        ### MISC ROLES ASSIGNMENT

        # User added reaction to the UPE Misc Roles Message in #additional-roles
        if payload.message_id == self.ROLE_SOCIAL_ASSIGNMENT_MESSAGE_ID:
            
            desired_user_role = None

            print(f"{payload.emoji} vs {self.emojis_misc[self.OPPORTUNITY_ROLE_NAME]}")

            #Reaction is for Opportunity Seekers:
            if str(payload.emoji) == self.emojis_misc[self.OPPORTUNITY_ROLE_NAME]:
                print("Opportunity")
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.OPPORTUNITY_ROLE_NAME)
            
            #Reaction is for Women In Tech:
            elif str(payload.emoji) == self.emojis_misc[self.WOMENINTECH_ROLE_NAME]:
                print("WIT")
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.WOMENINTECH_ROLE_NAME)
            
            #Reaction is for Fitness Crew:
            elif str(payload.emoji) == self.emojis_misc[self.FITNESSCREW_ROLE_NAME]:
                # Sets the verified 'Interested' role 
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.FITNESSCREW_ROLE_NAME)

            #Reaction is for Among Us:
            elif str(payload.emoji) == self.emojis_misc[self.AMONGUS_ROLE_NAME]:
                # Sets the verified 'Interested' role
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.AMONGUS_ROLE_NAME)

            #Reaction is for Tamagotchi Tamers:
            elif str(payload.emoji) == self.emojis_misc[self.TAMAGOTCHI_ROLE_NAME]:
                # Sets the verified 'Interested' role
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.TAMAGOTCHI_ROLE_NAME)

            #Reaction is for Pokemon Trainers:
            elif str(payload.emoji) == self.emojis_misc[self.POKE_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.POKE_ROLE_NAME)

            #Reaction is for Gacha Addicts:
            elif str(payload.emoji) == self.emojis_misc[self.GACHA_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.GACHA_ROLE_NAME)

            #Invalid reaction (unreachable condition)
            else:
                print("Unknown Reaction Added. Verify channel permissions.")
            
            if desired_user_role is not None:
                await reacting_user.remove_roles(desired_user_role) 
                print("User " + reacting_user.name + f" is interested in {desired_user_role}!")

    @commands.command()
    async def give_role(self, ctx, target_user: discord.Member, *args):
        
        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = ctx.guild.get_role(self.WHISPERER_ROLE_ID)

        if (mod_role not in roles) and (whisperer_role not in roles):
            await ctx.send(f'{ctx.author.mention} this command is only meant to be used by Moderators or Program Organizers.')

        else:
            desired_role = None

            if len(args) == 0:
                await ctx.send("You must include the full tag of the user followed by the name of the role")
            elif not isinstance(target_user, discord.Member):
                await ctx.send("You must include the full tag of the user (Ex. User#0000)")
            else:
                desired_role_name = (" ".join(args)).strip()
                desired_role = discord.utils.get(ctx.guild.roles, name=desired_role_name)

            if not desired_role:
                await ctx.send("Role couldn't not be found... Verify and try again!")
            else:
                await target_user.add_roles(desired_role)
                await ctx.send(f"{target_user.mention} has been assigned the {desired_role} role")
    
    @commands.command()
    async def take_role(self, ctx, target_user: discord.Member, *args):
        
        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = ctx.guild.get_role(self.WHISPERER_ROLE_ID)

        if (mod_role not in roles) and (whisperer_role not in roles):
            await ctx.send(f'{ctx.author.mention} this command is only meant to be used by Moderators or Program Organizers.')
      
        else:
            desired_role = None

            if len(args) == 0:
                await ctx.send("You must mention the user followed by the name of the role")
            elif not isinstance(target_user, discord.Member):
                await ctx.send("You must mention the target user with `@` ")
            else:
                desired_role_name = (" ".join(args)).strip()
                desired_role = discord.utils.get(ctx.guild.roles, name=desired_role_name)

            if not desired_role:
                await ctx.send("Role couldn't not be found... Verify and try again!")
            else:
                await target_user.remove_roles(desired_role)
                await ctx.send(f"the {desired_role} role has been removed from {target_user.mention}")

    @commands.command()
    async def purge_role(self, ctx, *args):
        
        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)

        if mod_role not in roles:
            await ctx.send(
                f'{ctx.author.mention} this command is only meant to be used by Moderators.')
        else:
            old_role = None

            if not args:
                await ctx.send("You must include the role name to be purged")
            else:
                role_name = " ".join(args)
                old_role = discord.utils.get(ctx.guild.roles, name=role_name)

            if not old_role:
                await ctx.send("Role couldn't not be found... Verify and try again!")
            else:
                await ctx.send(f"Attempting to purge the {old_role} from all members...")

                for member in ctx.guild.members:
                    if old_role in member.roles:
                        await member.remove_roles(old_role)

                await ctx.send(f"The {old_role} has been purged!")

    @commands.command()
    async def mass_add(self, ctx, *args):
        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)

        role_name_words = []
        is_mention_argument = False
        num_role_args = 0

        response_description = "Add Role: +"
        succesful_users = [] #List to hold the name of users who now have the role.
        failed_users = [] #List to hold the name of users who failed to acquire the role.

        if mod_role not in roles:
            await ctx.send(
                f'{ctx.author.mention} this command is only meant to be used by Moderators.')
        else:
            role = None

            if len(args) < 2:
                await ctx.send("You must include the name of the role and mention all the users")
            else:

                for arg in args:
                    if is_mention_argument:
                        pass
                    else:
                        if arg != '$':
                            role_name_words.append(arg)
                        else:
                            is_mention_argument = True #indicates the next args are users
                        num_role_args += 1

                role_name = " ".join(role_name_words)
                role = discord.utils.get(ctx.guild.roles, name=role_name)

            if not role:
                await ctx.send("Role couldn't not be found... Verify and try again!\nMake sure you're using `$` between the role and the users")
            else:
                response_description += f"{str(role)}"
                for member_name in args[num_role_args:]:
                    print(member_name)
                    try:
                        member = await commands.MemberConverter().convert(ctx, member_name)
                    except commands.BadArgument:
                        print(f"{member_name} is not a valid member or member ID.")
                        failed_users.append(member_name)
                    else:
                        await member.add_roles(role)
                        succesful_users.append(member.mention)

                response_succesful_users = ", ".join(succesful_users)
                response_failed_users = ", ".join(failed_users)
                has_failed_users = bool(failed_users)
                has_succesful_users = bool(succesful_users)

                if not has_failed_users:
                    response_title = "Done!"
                    embed_color = self.GREEN_HEX
                elif has_succesful_users:
                    response_title = "Done. Please Review."
                    embed_color = self.YELLOW_HEX 
                else:
                    response_title = "Failed..."
                    embed_color = self.RED_HEX

                embed_response = discord.Embed(title=response_title, description=response_description, color=embed_color)
                if has_succesful_users:
                    embed_response.add_field(name="Succesful on:", value=response_succesful_users, inline=False)
                if has_failed_users:
                    embed_response.add_field(name="Failed on:", value=response_failed_users, inline=False)

                await ctx.send(embed=embed_response)

    @commands.command()
    async def replace_role(self, ctx, *args):
        
        roles = ctx.author.roles
        mod_role = ctx.guild.get_role(self.MODERATOR_ROLE_ID)

        if mod_role not in roles:
            await ctx.send(
                f'{ctx.author.mention} this command is only meant to be used by Moderators.')
        else:
            old_role = None
            new_role = None

            if not args:
                await ctx.send("You must include the current role name, followed by the new role name ( Separated by a `$` )")
            else:
                roles_name = " ".join(args)
                roles_name_list = roles_name.split("$")

            if len(roles_name_list) < 2:
                await ctx.send("You must include the current role name, followed by the new role name ( Separated by a `$` )")
            else: 
                old_role = discord.utils.get(ctx.guild.roles, name=roles_name_list[0].strip())
                new_role = discord.utils.get(ctx.guild.roles, name=roles_name_list[1].strip())

            if not old_role and not new_role:
                await ctx.send("Roles couldn't not be found... Verify and try again!")
            else:
                await ctx.send(f"Attempting to give members with the {old_role} role the {new_role} role instead...")

                for member in ctx.guild.members:
                    if old_role in member.roles:
                        await member.add_roles(new_role)
                        await member.remove_roles(old_role)

                await ctx.send(f"Members that had the {old_role} role now have the {new_role} role instead!")

def setup(bot):
    bot.add_cog(Roles(bot)) 