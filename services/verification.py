import os

import disnake
from db.database import get_discord_id_role

VERIFIED_ROLE_ID = os.getenv("VERIFIED_ROLE_ID")


async def process_student_verification(
    guild: disnake.Guild | None, member: disnake.Member, full_name: str
) -> tuple[bool, str]:

    roles_to_add = []

    groups = await get_discord_id_role(full_name)
    if not groups:
        return False, "No group found for the specified student"

    if VERIFIED_ROLE_ID:
        v_role_id = guild.get_role(int(VERIFIED_ROLE_ID))
        if v_role_id:
            roles_to_add.append(v_role_id)

    if groups:
        g_role_id = guild.get_role(int(groups))
        if g_role_id:
            roles_to_add.append(g_role_id)

    if not roles_to_add:
        return False, "No roles to assign (check the role IDs in the config)"

    try:
        await member.add_roles(*roles_to_add, reason="Successful verification by full name")
    except disnake.Forbidden:
        return False, "The bot does not have permission to assign these roles"
    except disnake.HTTPException:
        return False, "Discord API error, please try again later"

    return True, "Roles granted successfully!"


async def remove_discord_role(
    inter: disnake.ApplicationCommandInteraction,
    discord_role_id: int | None,
    target_member: disnake.Member,
) -> bool:
    roles_to_remove = []

    if not inter.guild:
        return False

    verified_role = inter.guild.get_role(int(VERIFIED_ROLE_ID))
    if not verified_role or verified_role not in target_member.roles:
        pass
    else:
        roles_to_remove.append(verified_role)

    if discord_role_id:
        role = inter.guild.get_role(discord_role_id)
        if not role or role not in target_member.roles:
            pass
        else:
            roles_to_remove.append(role)

    if roles_to_remove:
        try:
            await target_member.remove_roles(
                *roles_to_remove, reason=f"Unverified by {inter.author}"
            )
            return True
        except (disnake.Forbidden, disnake.HTTPException):
            return False
    else:
        return True
