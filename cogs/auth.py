import os

import disnake
from db.database import find_student_by_name, register_student, unverify_student
from disnake.ext import commands
from services.verification import process_student_verification
from utils.i18n import t
from utils.security import is_admin

LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")


class RegisterModal(disnake.ui.Modal):

    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label=t("modal_name_label"),
                placeholder=t("modal_name_placeholder"),
                custom_id="full_name",
                style=disnake.TextInputStyle.short,
                max_length=100,
            )
        ]
        super().__init__(title=t("modal_title"), components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        input_name = inter.text_values["full_name"].strip().title()
        students = await find_student_by_name(input_name)

        if not students:
            await inter.response.send_message(
                t("not_in_lists"),
                ephemeral=True,
            )
            return

        if len(students) > 1:
            await inter.response.send_message(
                t("multiple_found"),
                ephemeral=True,
            )
            return

        student = students[0]

        if student["discord_id"] is not None:
            await inter.response.send_message(
                t("already_registered"), ephemeral=True
            )
            return

        db_success = await register_student(
            student_id=student["student_id"], discord_id=inter.author.id
        )

        if not db_success:
            await inter.response.send_message(
                t("db_error_register"), ephemeral=True
            )
            return

        _success, roles_msg = await process_student_verification(
            guild=inter.guild, member=inter.author, full_name=input_name
        )

        if not _success:
            await unverify_student(inter.author.id)
            await inter.response.send_message(
                t("reg_rollback_msg", error=roles_msg), ephemeral=True
            )
            return

        await inter.response.send_message(roles_msg, ephemeral=True)

        if inter.guild and LOG_CHANNEL_ID and LOG_CHANNEL_ID.strip().isdigit():
            log_channel = inter.guild.get_channel(int(LOG_CHANNEL_ID))
            if log_channel:
                try:
                    await log_channel.send(
                        t(
                            "log_verified",
                            member=inter.author.mention,
                            member_id=inter.author.id,
                            name=input_name,
                        )
                    )
                except (disnake.Forbidden, disnake.HTTPException):
                    pass


class RegisterView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label=t("btn_verify"),
        style=disnake.ButtonStyle.success,
        custom_id="reg_button",
    )
    async def register_button(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        await inter.response.send_modal(RegisterModal())


class AuthCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(RegisterView())

    @is_admin()
    @commands.slash_command(
        name="setup_reg", description=t("setup_reg_desc")
    )
    @commands.has_permissions(administrator=True)
    async def setup_reg(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title=t("embed_title"),
            description=t("embed_desc"),
            color=disnake.Color.green(),
        )
        embed.set_footer(text=t("embed_footer"))

        await inter.channel.send(embed=embed, view=RegisterView())
        await inter.response.send_message(t("setup_reg_success"), ephemeral=True)


def setup(bot: commands.InteractionBot):
    bot.add_cog(AuthCog(bot))
