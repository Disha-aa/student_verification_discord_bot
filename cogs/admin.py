import os

import disnake
from cogs.auth import process_student_verification
from db.database import (
    add_student,
    delete_user_from_db,
    get_role_id_by_discord_id,
    get_student_by_discord_id,
    unverify_student,
    update_student_role,
)
from disnake.ext import commands
from services.verification import remove_discord_role
from utils.security import is_admin, is_owner

LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    async def cog_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, error: Exception
    ) -> None:
        if isinstance(error, commands.CheckFailure):
            await inter.response.send_message(str(error), ephemeral=True)

    @commands.slash_command(
        name="grant_admin",
        description="Grant admin rights to a user",
    )
    @is_owner()
    async def grant_admin(
        self,
        inter: disnake.ApplicationCommandInteraction,
        target_member: disnake.Member,
    ) -> bool:
        student = await get_student_by_discord_id(target_member.id)
        if not student:
            await inter.response.send_message(
                f"{target_member.mention} has not been verified yet", ephemeral=True
            )
            return False

        current_role = student["user_role"]

        if current_role == "admin":
            await inter.response.send_message(
                f"{target_member.mention} already has the admin role", ephemeral=True
            )
            return False

        success = await update_student_role(
            discord_id=target_member.id, new_role="admin"
        )

        if not success:
            await inter.response.send_message(
                "Failed to update the role in the database", ephemeral=True
            )
            return False
        await inter.response.send_message(
            f"User {target_member.mention} was successfully granted the **admin** role in the database!",
            ephemeral=True,
        )
        return True

    @commands.slash_command(
        name="verification_user",
        description="Verify a student",
    )
    @is_admin()
    async def verification_user(
        self,
        inter: disnake.ApplicationCommandInteraction,
        target_member: disnake.Member,
        full_name: str,
        group_num: int,
    ) -> None:
        full_name = full_name.strip().title()
        await inter.response.defer(ephemeral=True)

        if not (
            1 <= group_num <= 9
        ):  # I have 9 classes at university—so the grading scale is from 1 to 10
            await inter.edit_original_response(content=("We only have 9 groups"))
            return

        if len(full_name.strip().split()) < 2:
            await inter.edit_original_response(content=("Enter the full name"))
            return

        student = await get_student_by_discord_id(target_member.id)
        if student:
            await inter.edit_original_response(
                content=(f"{target_member.mention} has already been verified")
            )
            return

        success = await add_student(
            full_name=full_name, user_group=group_num, discord_id=target_member.id
        )

        if not success:
            await inter.edit_original_response(
                content=("Database error: failed to add the record")
            )
            return
        role_success, role_msg = await process_student_verification(
            guild=inter.guild, member=target_member, full_name=full_name
        )

        if not role_success:
            await inter.edit_original_response(
                content=(
                    f"The record was created, but an error occurred with the roles: {role_msg}"
                )
            )
            return

        await inter.edit_original_response(
            content=(
                f"Student {full_name} was successfully linked to {target_member.mention}, roles granted"
            )
        )

        if inter.guild:
            log_channel = inter.guild.get_channel(int(LOG_CHANNEL_ID))
            if log_channel:
                try:
                    await log_channel.send(
                        f"Administrator {inter.author.mention} manually verified "
                        f"user {target_member.mention} (`{target_member.id}`) "
                        f"as: **{full_name}** | Group: **{group_num}**"
                    )
                except (disnake.Forbidden, disnake.HTTPException):
                    pass

    @commands.slash_command(
        name="unverify_user", description="Revoke a user's verification"
    )
    @is_admin()
    async def unverify_user(
        self,
        inter: disnake.ApplicationCommandInteraction,
        target_member: disnake.Member,
    ) -> None:
        await inter.response.defer(ephemeral=True)

        discord_role_id = await get_role_id_by_discord_id(target_member.id)

        is_unverified = await unverify_student(target_member.id)
        if not is_unverified:
            await inter.edit_original_response(
                content=(f"User {target_member.mention} was not found in the database")
            )
            return

        role_removed = await remove_discord_role(inter, discord_role_id, target_member)
        if not role_removed:
            await inter.edit_original_response(
                content=(
                    f"Verification for user {target_member.mention} was successfully revoked, "
                    "but the role could not be removed (check permissions or whether the role exists)"
                )
            )
        else:
            await inter.edit_original_response(
                content=(f"Verification for {target_member.mention} has been revoked")
            )

            if inter.guild:
                log_channel = inter.guild.get_channel(int(LOG_CHANNEL_ID))
                if log_channel:
                    try:
                        await log_channel.send(
                            f"Administrator {inter.author.mention} revoked verification "
                            f"for user {target_member.mention} (`{target_member.id}`)"
                        )
                    except (disnake.Forbidden, disnake.HTTPException):
                        pass

    @commands.slash_command(
        name="delete_user", description="Delete a user from the database"
    )
    @is_admin()
    async def delete_user(
        self,
        inter: disnake.ApplicationCommandInteraction,
        target_member: disnake.Member,
    ) -> None:
        await inter.response.defer(ephemeral=True)

        discord_role_id = await get_role_id_by_discord_id(target_member.id)

        is_deleted = await delete_user_from_db(target_member.id)
        if not is_deleted:
            await inter.edit_original_response(
                content=(f"User {target_member.mention} was not found in the database")
            )
            return

        role_removed = await remove_discord_role(inter, discord_role_id, target_member)

        if not role_removed:
            await inter.edit_original_response(
                content=(
                    f"User {target_member.mention} was successfully deleted from the database, but the role"
                    " could not be removed (check permissions or whether the role exists)"
                )
            )

        else:
            await inter.edit_original_response(
                content=(
                    f"User {target_member.mention} was successfully deleted from the database"
                )
            )

            if inter.guild:
                log_channel = inter.guild.get_channel(int(LOG_CHANNEL_ID))
                if log_channel:
                    try:
                        await log_channel.send(
                            f"Administrator {inter.author.mention} deleted "
                            f"user {target_member.mention} (`{target_member.id}`) from the database"
                        )
                    except (disnake.Forbidden, disnake.HTTPException):
                        pass


def setup(bot: commands.InteractionBot):
    bot.add_cog(AdminCog(bot))
