import os

import disnake
from db.database import get_discord_id_role
from utils.i18n import t

VERIFIED_ROLE_ID = os.getenv("VERIFIED_ROLE_ID")


async def process_student_verification(
    guild: disnake.Guild | None, member: disnake.Member, full_name: str
) -> tuple[bool, str]:
    if not guild:
        return False, t("guild_not_found")

    roles_to_add = []

    groups = await get_discord_id_role(full_name)
    if not groups:
        return False, t("group_not_found")

    if VERIFIED_ROLE_ID and VERIFIED_ROLE_ID.strip().isdigit():
        v_role_id = guild.get_role(int(VERIFIED_ROLE_ID))
        if v_role_id:
            roles_to_add.append(v_role_id)

    if groups:
        g_role_id = guild.get_role(int(groups))
        if g_role_id:
            roles_to_add.append(g_role_id)

    if not roles_to_add:
        return False, t("roles_empty")

    try:
        await member.add_roles(*roles_to_add, reason=t("role_reason"))
    except disnake.Forbidden:
        return False, t("bot_no_perms")
    except disnake.HTTPException:
        return False, t("api_error")

    return True, t("roles_granted")


async def remove_discord_role(
    inter: disnake.ApplicationCommandInteraction,
    discord_role_id: int | None,
    target_member: disnake.Member,
) -> bool:
    roles_to_remove = []

    if not inter.guild:
        return False

    if VERIFIED_ROLE_ID and VERIFIED_ROLE_ID.strip().isdigit():
        verified_role = inter.guild.get_role(int(VERIFIED_ROLE_ID))
        if verified_role and verified_role in target_member.roles:
            roles_to_remove.append(verified_role)

    if discord_role_id:
        role = inter.guild.get_role(discord_role_id)
        if role and role in target_member.roles:
            roles_to_remove.append(role)

    if roles_to_remove:
        try:
            await target_member.remove_roles(
                *roles_to_remove, reason=t("unverify_reason", author=inter.author)
            )
            return True
        except (disnake.Forbidden, disnake.HTTPException):
            return False
    else:
        return True
