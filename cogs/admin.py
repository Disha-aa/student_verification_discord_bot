import os

import disnake
from db.database import (
    add_student,
    delete_user_from_db,
    get_role_id_by_discord_id,
    get_student_by_discord_id,
    unverify_student,
    update_student_role,
)
from disnake.ext import commands
from services.verification import process_student_verification, remove_discord_role
from utils.i18n import t
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
        description=t("grant_admin_desc"),
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
                t("not_verified_yet", member=target_member.mention), ephemeral=True
            )
            return False

        current_role = student["user_role"]

        if current_role == "admin":
            await inter.response.send_message(
                t("already_has_admin", member=target_member.mention), ephemeral=True
            )
            return False

        success = await update_student_role(
            discord_id=target_member.id, new_role="admin"
        )

        if not success:
            await inter.response.send_message(
                t("db_role_update_failed"), ephemeral=True
            )
            return False
        await inter.response.send_message(
            t("grant_admin_success", member=target_member.mention),
            ephemeral=True,
        )
        return True

    @commands.slash_command(
        name="verification_user",
        description=t("verify_user_desc"),
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

        if not (1 <= group_num <= 9):
            await inter.edit_original_response(content=t("invalid_group"))
            return

        if len(full_name.strip().split()) < 2:
            await inter.edit_original_response(content=t("enter_full_name"))
            return

        student = await get_student_by_discord_id(target_member.id)
        if student:
            await inter.edit_original_response(
                content=t("user_already_verified", member=target_member.mention)
            )
            return

        success = await add_student(
            full_name=full_name, user_group=group_num, discord_id=target_member.id
        )

        if not success:
            await inter.edit_original_response(
                content=t("db_insert_error")
            )
            return
        role_success, role_msg = await process_student_verification(
            guild=inter.guild, member=target_member, full_name=full_name
        )

        if not role_success:
            await inter.edit_original_response(
                content=t("manual_verify_role_err", error=role_msg)
            )
            return

        await inter.edit_original_response(
            content=t("manual_verify_success", name=full_name, member=target_member.mention)
        )

        if inter.guild and LOG_CHANNEL_ID and LOG_CHANNEL_ID.strip().isdigit():
            log_channel = inter.guild.get_channel(int(LOG_CHANNEL_ID))
            if log_channel:
                try:
                    await log_channel.send(
                        t(
                            "log_manual_verify",
                            author=inter.author.mention,
                            member=target_member.mention,
                            member_id=target_member.id,
                            name=full_name,
                            group=group_num,
                        )
                    )
                except (disnake.Forbidden, disnake.HTTPException):
                    pass

    @commands.slash_command(
        name="unverify_user", description=t("unverify_desc")
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
                content=t("user_not_found_db", member=target_member.mention)
            )
            return

        role_removed = await remove_discord_role(inter, discord_role_id, target_member)
        if not role_removed:
            await inter.edit_original_response(
                content=t("unverify_role_err", member=target_member.mention)
            )
        else:
            await inter.edit_original_response(
                content=t("unverify_success", member=target_member.mention)
            )

            if inter.guild and LOG_CHANNEL_ID and LOG_CHANNEL_ID.strip().isdigit():
                log_channel = inter.guild.get_channel(int(LOG_CHANNEL_ID))
                if log_channel:
                    try:
                        await log_channel.send(
                            t(
                                "log_unverify",
                                author=inter.author.mention,
                                member=target_member.mention,
                                member_id=target_member.id,
                            )
                        )
                    except (disnake.Forbidden, disnake.HTTPException):
                        pass

    @commands.slash_command(
        name="delete_user", description=t("delete_user_desc")
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
                content=t("user_not_found_db", member=target_member.mention)
            )
            return

        role_removed = await remove_discord_role(inter, discord_role_id, target_member)

        if not role_removed:
            await inter.edit_original_response(
                content=t("delete_role_err", member=target_member.mention)
            )
        else:
            await inter.edit_original_response(
                content=t("delete_success", member=target_member.mention)
            )

            if inter.guild and LOG_CHANNEL_ID and LOG_CHANNEL_ID.strip().isdigit():
                log_channel = inter.guild.get_channel(int(LOG_CHANNEL_ID))
                if log_channel:
                    try:
                        await log_channel.send(
                            t(
                                "log_delete",
                                author=inter.author.mention,
                                member=target_member.mention,
                                member_id=target_member.id,
                            )
                        )
                    except (disnake.Forbidden, disnake.HTTPException):
                        pass


def setup(bot: commands.InteractionBot):
    bot.add_cog(AdminCog(bot))
