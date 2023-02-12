import discord
from discord.ext import commands
from discord import app_commands
import config


class Roles(commands.GroupCog, name="roles"):

    '''
    Review, add or remove roles
    '''

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.MODERATOR_ROLE_ID = 399551100799418370 if config.isProd else 1065042154407338039
        # Additional role for Eboard and Committee members to manage certain
        # commands.
        self.WHISPERER_ROLE_ID = 797617839355854848

        # Channels
        self.BOT_LOGS_CHANNEL_ID = 626541886533795850
        self.log_channel = self.bot.get_channel(self.BOT_LOGS_CHANNEL_ID)

        # Messages
        # CHANGE THIS FOR EVENTS. (like Global Game Jam, PantherHacks and
        # ShellHacks!)
        self.ROLE_EVENT_ASSIGNMENT_MESSAGE_ID = 804525065420668958
        self.ROLE_UPE_ASSIGNMENT_MESSAGE_ID = 798334433957773343
        self.ROLE_SOCIAL_ASSIGNMENT_MESSAGE_ID = 798334792349384714

        # Colors HEX
        self.BLUE_HEX = 0x3895D3
        self.GREEN_HEX = 0x238823
        self.YELLOW_HEX = 0xFFBF00
        self.RED_HEX = 0xD2222D

    @app_commands.command(name="see",
                          description="Used to inquire about a role.")
    async def see(self, interaction: discord.Interaction, role: discord.Role):

        '''
        Used to inquire about a role. Ex: ?seerole Code Member
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
            response_description += f'{interaction.user.mention} this command is only meant to be used by Moderators or Program Organizers'
        else:
            if not role:
                response_description += f'Role "{role_name}"could not be found... Verify and try again!'
            else:
                for member in interaction.guild.members:
                    if role in member.roles:
                        role_members.append(str(member))
                        role_members_count += 1

                role_members.append("───────")
                is_success = True

        if is_success:
            response_title = "Role Info"
            response_description = f"**Name:** *{str(role)}*\n**Position:** {role.position}\n**Hoisted:** {role.hoist}\n**Mentionable:** {role.mentionable}\n**ID:** {role.id}\n**Creation Date:** {role.created_at.date()}"
            # TODO: Implement Pagination with Discord Reactions.
            response_users = "\n".join(role_members[:15])
            embed_color = role.color

        embed_response = discord.Embed(
            title=response_title,
            description=response_description,
            color=embed_color)
        embed_response.add_field(
            name=f"Users: ({role_members_count})",
            value=response_users,
            inline=False)
        await interaction.response.send_message(embed=embed_response)

    @app_commands.command(name="give",
                          description="Used to assign a role to a user.")
    async def give(self, interaction: discord.Interaction, user: discord.User, role: discord.Role):
        '''
        Used to assign a role to a user. Ex: ?giverole @Laro#0001 Code Member
        '''
        is_success = False
        response_description = f"<a:utilfailure:809713365088993291> "
        embed_color = self.RED_HEX

        roles = interaction.user.roles
        mod_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = interaction.guild.get_role(self.WHISPERER_ROLE_ID)

        if (mod_role not in roles) and (whisperer_role not in roles):
            response_description += f'This command is only meant to be used by Moderators or Program Organizers'
        else:
            try:
                await user.add_roles(role)
                is_success = True
            except Exception as error:
                response_description += f'Action failed: {error}'

        if is_success:
            response_description = f"<a:verified:798786443903631360> Added Role: + {str(role)} to {user.mention}"
            embed_color = self.GREEN_HEX

        embed_response = discord.Embed(
            title=None,
            description=response_description,
            color=embed_color)
        await interaction.response.send_message(embed=embed_response, ephemeral=not is_success)

    @app_commands.command(name="take",
                          description="Used to remove a role to a user.")
    async def take(self, interaction: discord.Interaction, user: discord.User, role: discord.Role):

        '''
        Used to remove a role to a user. Ex: ?takerole @Laro#0001 InfoTech Member
        '''
        is_success = False
        response_description = f"<a:utilfailure:809713365088993291> "
        embed_color = self.RED_HEX

        roles = interaction.user.roles
        mod_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = interaction.guild.get_role(self.WHISPERER_ROLE_ID)

        if (mod_role not in roles) and (whisperer_role not in roles):
            response_description += f'This command is only meant to be used by Moderators or Program Organizers'
        else:
            if role not in user.roles:
                response_description += f"User {user} did not have the {role} role."
            else:
                try:
                    await user.remove_roles(role)
                    is_success = True
                except Exception as error:
                    response_description += f'<a:utilfailure:809713365088993291> Action failed: {error}'

            if is_success:
                response_description = f"<a:verified:798786443903631360> Removed Role: - {role} from {user.mention}"
                embed_color = self.GREEN_HEX

        embed_response = discord.Embed(
            title=None,
            description=response_description,
            color=embed_color)
        await interaction.response.send_message(embed=embed_response, ephemeral=not is_success)

    @app_commands.command(name="wash",
                          description="Removes the specified role from ALL users.")
    @commands.has_permissions(administrator=True)
    async def wash(self, interaction: discord.Interaction, role: discord.Role):

        '''
        Removes the specified role from ALL users.
        '''

        is_success = False
        response_description = f"<a:utilfailure:809713365088993291> "
        embed_color = self.RED_HEX

        roles = interaction.user.roles
        mod_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)

        if mod_role not in roles:
            response_description += f'This command is only meant to be used by Moderators'
        else:
            response_description = f"Attempting to purge the {role} from all members..."
            embed_response = discord.Embed(
                title="<a:utilloading:809712534961389649> In Progress...",
                description=response_description,
                color=self.YELLOW_HEX)
            response = interaction.response.send_message(
                embed=embed_response, ephemeral=True)

            counter = 0

            for member in interaction.guild.members:
                if role in member.roles:
                    try:
                        await member.remove_roles(role)
                        counter += 1
                    except BaseException:
                        pass

            is_success = True if counter > 0 else False

        if is_success:
            response_description = f"<a:verified:798786443903631360> Purged Role: :toilet: {str(old_role)} from **All Users**"
            embed_color = self.GREEN_HEX

        embed_response = discord.Embed(
            title=None,
            description=response_description,
            color=embed_color)
        await interaction.response.send_message(embed=embed_response, ephemeral=not is_success)

    @app_commands.command(name="distribute",
                          description="Used to add the same role to multiple users.")
    async def distribute(self,
                         interaction: discord.Interaction,
                         role: discord.Role,
                         user1: discord.User,
                         user2: discord.User,
                         user3: discord.User,
                         user4: discord.User,
                         user5: discord.User,
                         user6: discord.User,
                         user7: discord.User,
                         user8: discord.User,
                         user9: discord.User,
                         user10: discord.User,
                         user11: discord.User,
                         user12: discord.User,
                         ):
        '''
        Used to add the same role to multiple users.
        '''
        is_success = False
        response_title = None
        response_description = f"<a:utilfailure:809713365088993291> "
        has_succesful_users = False
        has_failed_users = False
        embed_color = self.RED_HEX

        roles = interaction.user.roles
        mod_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = interaction.guild.get_role(self.WHISPERER_ROLE_ID)

        if (mod_role not in roles) and (whisperer_role not in roles):
            response_description += f'This command is only meant to be used by Moderators or Program Organizers'
        else:
            response_description = f"Attempting to assign the {str(role)} role to multiple users"
            embed_response = discord.Embed(
                title="<a:utilloading:809712534961389649> In Progress...",
                description=response_description,
                color=self.YELLOW_HEX)
            response = await interaction.response.send_message(embed=embed_response, ephemeral=False)

            users = [
                user1,
                user2,
                user3,
                user4,
                user5,
                user6,
                user7,
                user8,
                user9,
                user10,
                user11,
                user12]
            # List to hold the name of users who now have the role.
            succesful_users = []
            # List to hold the name of users who failed to acquire the role.
            failed_users = []

            for user in users:
                try:
                    await user.add_roles(role)
                    succesful_users.append(user)
                except BaseException:
                    failed_users.append(user)

            is_success = True

            # Final Response
            response_description = f"Added Role: +{str(role)}"
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
            embed_response = discord.Embed(
                title=response_title,
                description=response_description,
                color=embed_color)
            if has_succesful_users:
                title = "Succesful on: "
                value = ""
                for successful_user in succesful_users:
                    value += f"{successful_user.mention}, "
                embed_response.add_field(
                    name=title,
                    value=value,
                    inline=False)
            if has_failed_users:
                title = "Failed on: "
                value = ""
                for failed_user in failed_users:
                    value += f"{failed_user.mention}, "
                embed_response.add_field(
                    name=title,
                    value=value,
                    inline=False)
            await interaction.edit_original_response(embed=embed_response)
        else:
            embed_response = discord.Embed(
                title=response_title,
                description=response_description,
                color=embed_color)
            await interaction.response.send_message(embed=embed_response, ephemeral=not is_success)

    @app_commands.command(name="spread",
                          description="Like distribute but for a comma separated copy-pasta. Can be more effective but has less guardrails.")
    async def spread(self, interaction: discord.Interaction, role: discord.Role, pasta: str):
        '''
        Like distribute but for a comma separated copy-pasta. Can be more effective but has less guardrails.
        '''
        is_success = False
        response_title = None
        response_description = f"<a:utilfailure:809713365088993291> "
        has_succesful_users = False
        has_failed_users = False
        embed_color = self.RED_HEX

        roles = interaction.user.roles
        mod_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)
        whisperer_role = interaction.guild.get_role(self.WHISPERER_ROLE_ID)

        if (mod_role not in roles) and (whisperer_role not in roles):
            response_description += f'This command is only meant to be used by Moderators or Program Organizers'
        else:
            response_description = f"Attempting to assign the {str(role)} role to multiple users"
            embed_response = discord.Embed(
                title="<a:utilloading:809712534961389649> In Progress...",
                description=response_description,
                color=self.YELLOW_HEX)
            await interaction.response.send_message(embed=embed_response, ephemeral=False)

            # List to hold the name of users who now have the role.
            succesful_users = []
            # List to hold the name of users who failed to acquire the role.
            failed_users = []

            member_names = pasta.split(',')

            for member_name in member_names:
                try:
                    member_name_parts = member_name.split('#')
                    print(member_name_parts)
                    is_user_id = len(
                        member_name_parts) == 1 and member_name_parts[0].strip().isnumeric()
                    if is_user_id:
                        member = await interaction.guild.fetch_member(int(member_name_parts[0].strip()))
                    else:  # assume it's a username
                        if len(member_name_parts) <= 1:
                            raise commands.BadArgument
                        member = discord.utils.get(
                            interaction.guild.members,
                            name=member_name_parts[0].strip(),
                            discriminator=member_name_parts[1].strip())
                except (commands.BadArgument, commands.MemberNotFound, discord.errors.NotFound) as error:
                    failed_users.append(member_name)
                else:
                    if member is None:
                        failed_users.append(member_name)
                    else:
                        await member.add_roles(role)
                        succesful_users.append(member.mention)

            is_success = True

            # Final Response
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
                embed_response = discord.Embed(
                    title=response_title,
                    description=response_description,
                    color=embed_color)
                if has_succesful_users:
                    embed_response.add_field(
                        name="Succesful on:",
                        value=response_succesful_users,
                        inline=False)
                if has_failed_users:
                    embed_response.add_field(
                        name="Failed on:", value=response_failed_users, inline=False)
                await interaction.edit_original_response(embed=embed_response)
            else:
                embed_response = discord.Embed(
                    title=response_title,
                    description=response_description,
                    color=embed_color)
                await interaction.edit_original_response(embed=embed_response)

    @ app_commands.command(name="swap",
                           description="Used to replace a role for another on every user.")
    @ commands.has_permissions(administrator=True)
    async def swap(self, interaction: discord.Interaction, old_role: discord.User, new_role: discord.User):
        '''
        Used to replace a role for another on every user.\nEx: ?replacerole ShellHacks Hacker | ShellHacks 2018 Hacker
        '''
        is_success = False
        response_title = f"<a:utilfailure:809713365088993291> Failed"
        response_description = None
        embed_color = self.RED_HEX

        roles = interaction.user.roles
        mod_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)

        if mod_role not in roles:
            response_description += f'This command is only meant to be used by Moderators.'
        else:
            response_description = f"Attempting to give members with the {old_role} role the {new_role} role instead..."
            embed_response = discord.Embed(
                title="<a:utilloading:809712534961389649> In Progress...",
                description=response_description,
                color=self.YELLOW_HEX)
            response = await interaction.response.send_message(embed=embed_response, ephemeral=False)

            counter = 0
            has_failures = False
            # List to hold the name of users who failed to acquire the role.
            failed_users = []

            for member in interaction.guild.members:
                if old_role in member.roles:
                    try:
                        await member.add_roles(new_role)
                        await member.remove_roles(old_role)
                        counter += 1
                    except Exception as error:
                        has_failures = True
                        pass

            is_success = True if counter > 0 else False

        if is_success:
            response_description = f"Replaced Role: {old_role} :arrow_right: {new_role}"
            if has_failures:
                response_title = "<a:verified:798786443903631360> Done. Please Review."
                embed_color = self.YELLOW_HEX
                embed_response = discord.Embed(
                    title=response_title,
                    description=response_description,
                    color=embed_color)
                embed_response.add_field(
                    name="Succesful On:",
                    value=f'{counter} users',
                    inline=False)
                embed_response.add_field(
                    name="Failed on:",
                    value=response_failed_users,
                    inline=False)
            else:
                response_title = "<a:verified:798786443903631360> Done!"
                embed_color = self.GREEN_HEX
                embed_response = discord.Embed(
                    title=response_title,
                    description=response_description,
                    color=embed_color)
            await interaction.edit_original_response(embed=embed_response)

        else:
            embed_response = discord.Embed(
                title=response_title,
                description=response_description,
                color=embed_color)
            await interaction.response.send_message(embed=embed_response)

    @ app_commands.command(name="adjoin",
                           description="Used to replace a role for another on every user.")
    @ commands.has_permissions(administrator=True)
    async def adjoin(self, interaction: discord.Interaction, old_role: discord.User, new_role: discord.User):
        '''
        Used to replace a role for another on every user.\nEx: ?replacerole ShellHacks Hacker | ShellHacks 2018 Hacker
        '''
        is_success = False
        response_title = f"<a:utilfailure:809713365088993291> Failed"
        response_description = None
        embed_color = self.RED_HEX

        roles = interaction.user.roles
        mod_role = interaction.guild.get_role(self.MODERATOR_ROLE_ID)

        if mod_role not in roles:
            response_description += f'This command is only meant to be used by Moderators.'
        else:
            response_description = f"Attempting to give members with the {old_role} role the additional {new_role} role..."
            embed_response = discord.Embed(
                title="<a:utilloading:809712534961389649> In Progress...",
                description=response_description,
                color=self.YELLOW_HEX)
            response = await interaction.response.send_message(embed=embed_response, ephemeral=False)

            counter = 0
            has_failures = False
            # List to hold the name of users who failed to acquire the role.
            failed_users = []

            for member in interaction.guild.members:
                if old_role in member.roles:
                    try:
                        await member.add_roles(new_role)
                        counter += 1
                    except Exception as error:
                        has_failures = True
                        pass

            is_success = True if counter > 0 else False

        if is_success:
            response_description = f"Adjoined Roles in Members: {old_role} ➕ {new_role}"
            if has_failures:
                response_title = "<a:verified:798786443903631360> Done. Please Review."
                embed_color = self.YELLOW_HEX
                embed_response = discord.Embed(
                    title=response_title,
                    description=response_description,
                    color=embed_color)
                embed_response.add_field(
                    name="Succesful On:",
                    value=f'{counter} users',
                    inline=False)
                embed_response.add_field(
                    name="Failed on:",
                    value=response_failed_users,
                    inline=False)
            else:
                response_title = "<a:verified:798786443903631360> Done!"
                embed_color = self.GREEN_HEX
                embed_response = discord.Embed(
                    title=response_title,
                    description=response_description,
                    color=embed_color)
            await interaction.edit_original_response(embed=embed_response)

        else:
            embed_response = discord.Embed(
                title=response_title,
                description=response_description,
                color=embed_color)
            await interaction.response.send_message(embed=embed_response)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roles(bot))
