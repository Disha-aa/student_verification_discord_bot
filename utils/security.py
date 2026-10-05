import disnake
from db.database import get_student_by_discord_id
from disnake.ext import commands
from utils.i18n import t


def is_owner():
    async def predicate(inter: disnake.ApplicationCommandInteraction) -> bool:
        if inter.guild and inter.author.id == inter.guild.owner_id:
            return True

        student = await get_student_by_discord_id(inter.author.id)
        if student and student["user_role"] == "owner":
            return True
        raise commands.CheckFailure(t("only_owner"))

    return commands.check(predicate)


def is_admin():
    async def decorator(inter: disnake.ApplicationCommandInteraction) -> bool:
        if inter.author.guild_permissions.administrator:
            return True

        student = await get_student_by_discord_id(inter.author.id)
        if student and student["user_role"] in ("admin", "owner"):
            return True
        raise commands.CheckFailure(t("only_admin"))

    return commands.check(decorator)
