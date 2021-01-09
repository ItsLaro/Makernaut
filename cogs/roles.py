import discord
from discord.ext import commands

class Roles(commands.Cog):

    '''
    Handles user verification by reacting to the roles and assignment of other roles via reactions
    '''
    def __init__(self, bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370

        #Channels
        self.BOT_LOGS_CHANNEL_ID = 789520898356412477
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)

        #Messages
        self.RULES_ACCEPTANCE_MESSAGE_ID = 797210701604978698
        self.ROLE_UPE_ASSIGNMENT_MESSAGE_ID = 797208810577723402
        self.ROLE_SOCIAL_ASSIGNMENT_MESSAGE_ID = 797213192811053147
        
        #Roles
        self.CODE_ROLE_NAME = "Code"
        self.MAKE_ROLE_NAME = "Make"
        self.INFOTECH_ROLE_NAME = "Infotech"
        self.DESIGN_ROLE_NAME = "Design"
        self.ADVANCE_ROLE_NAME = "Advance"
        self.IGNITE_ROLE_NAME = "Ignite"
        self.SPARKDEV_ROLE_NAME = "Sparkdev"
        self.MENTOR_ROLE_NAME = "Mentor"
        self.SHELLHACKS_ROLE_NAME = "Shellhacks"
        self.DISCOVER_ROLE_NAME = "Discover"

        #Emojis
        self.emoji_rules = '\N{WHITE HEAVY CHECK MARK}'
        self.emojis_upe = {
            self.CODE_ROLE_NAME : "<:code:753692446738612384>",
            self.MAKE_ROLE_NAME : "<:make:753692447044927518>",
            self.INFOTECH_ROLE_NAME :"<:infotech:753692446726029388>",
            self.DESIGN_ROLE_NAME : "<:design:797279164548907029>",
            self.ADVANCE_ROLE_NAME : "<:advance:753692446776361126>",
            self.IGNITE_ROLE_NAME : "<:ignite:753692446801789039>",
            self.SPARKDEV_ROLE_NAME : "<:sparkdev:753692446784880760>",
            self.MENTOR_ROLE_NAME : "<:mentor:753692446776623284>",
            self.SHELLHACKS_ROLE_NAME : "<:shellhacks:753692446621433927>",
            self.DISCOVER_ROLE_NAME : "<:discover:753692446524702782>",
        }
        self.emojis_misc = {
            "OPPORTUNITIES" : "",
            "WOMENINTECH" : "",
            "FITNESSCREW" : "",
            "AMONGUS" : "",
            "GACHA" : "",
            "TAMAGOTCHI" : ""
        }

    #Events
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        reacting_user = payload.member

        ### RULES ACCEPTANCE
    
        # User added reaction to the Rules Acceptance Message in #welcome
        if payload.message_id == self.RULES_ACCEPTANCE_MESSAGE_ID:

            # User reacted with the appropiate emoji
            if payload.emoji.name == self.emoji_rules:
                # Sets the verified 'User' role
                verified_user_role = discord.utils.get(reacting_user.guild.roles, name="User")
                await reacting_user.add_roles(verified_user_role) 

                #Prints to console and notifies bot-log channel
                print("User " + reacting_user.name + " has read and accepted the rules!")
                await self.log_channel.send(f'{reacting_user.mention} has read and accepted the rules!')

        ### UPE ROLES ASSIGNMENT

        # User added reaction to the UPE Roles Message in #roles
        if payload.message_id == self.ROLE_UPE_ASSIGNMENT_MESSAGE_ID:
            
            desired_user_role = None

            #Reaction is for Code:
            if str(payload.emoji) == self.emojis_upe[self.CODE_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.CODE_ROLE_NAME)
            
            #Reaction is for Make:
            elif str(payload.emoji) == self.emojis_upe[self.MAKE_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.MAKE_ROLE_NAME)
            
            #Reaction is for Infotech:
            elif str(payload.emoji) == self.emojis_upe[self.INFOTECH_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.INFOTECH_ROLE_NAME)

            #Reaction is for Design:
            elif str(payload.emoji) == self.emojis_upe[self.DESIGN_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.DESIGN_ROLE_NAME)

            #Reaction is for Advance:
            elif str(payload.emoji) == self.emojis_upe[self.ADVANCE_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
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
            elif str(payload.emoji) == self.emojis_upe[self.CODE_ROLE_NAME]:
                # Sets the verified 'Interested' role (placeholder)
                desired_user_role = discord.utils.get(reacting_user.guild.roles, name=self.DISCOVER_ROLE_NAME)

            #Invalid reaction (unreachable condition)
            else:
                pass
            
            if desired_user_role is not None:
                await reacting_user.add_roles(desired_user_role) 
                #Prints to console and notifies bot-log channel
                print("User " + reacting_user.name + f" is interested in {desired_user_role}!")
                await self.log_channel.send(f'{self.emojis_upe[str(desired_user_role)]} {reacting_user.mention} is interested in {desired_user_role}!')

    @commands.command()
    async def substitute_role(self, ctx, *args):

        old_role = None
        new_role = None

        if not args:
            await ctx.send("You must include the current role name, followed by the new role name ( Separated by a `|` )")
        else:
            roles = " ".join(args)
            roles_list = roles.split("|")

        if len(roles_list) < 2:
            await ctx.send("You must include the current role name, followed by the new role name ( Separated by a `|` )")
        else: 
            print(roles_list[0].strip())
            old_role = discord.utils.get(ctx.guild.roles, name=roles_list[0].strip())
            new_role = discord.utils.get(ctx.guild.roles, name=roles_list[1].strip())

        if not old_role and not new_role:
            await ctx.send("Roles couldn't not be found... Verify and try again!")
        else:
            for member in ctx.guild.members:
                print(member)
                for role in member.roles: 
                    print(role)
                    if role == old_role: 
                        await member.add_roles(new_role)
                        await member.remove_roles(old_role)

            await ctx.send(f"Members that had the {old_role} role now have the {new_role} role instead")

def setup(bot):
    bot.add_cog(Roles(bot)) 