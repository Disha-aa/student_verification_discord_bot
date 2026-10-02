import disnake
from db.database import get_student_by_discord_id
from disnake.ext import commands


def is_owner():
    async def predicate(inter: disnake.ApplicationCommandInteraction) -> bool:
        student = await get_student_by_discord_id(inter.author.id)
        if student and student["user_role"] == "owner":
            return True
        raise commands.CheckFailure("This command is only available to the Owner!")

    return commands.check(predicate)


def is_admin():
    async def decorator(inter: disnake.ApplicationCommandInteraction) -> bool:
        student = await get_student_by_discord_id(inter.author.id)
        if student and student["user_role"] in ("admin", "owner"):
            return True
        raise commands.CheckFailure("This command is only available to admins!")

    return commands.check(decorator)
