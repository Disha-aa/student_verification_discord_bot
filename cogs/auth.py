import os

import disnake
from db.database import find_student_by_name, register_student
from disnake.ext import commands
from services.verification import process_student_verification
from utils.security import is_admin

VERIFIED_ROLE_ID = os.getenv("VERIFIED_ROLE_ID")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")


class RegisterModal(disnake.ui.Modal):

    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Enter your full name",
                placeholder="Last name First name Patronymic",
                custom_id="full_name",
                style=disnake.TextInputStyle.short,
                max_length=100,
            )
        ]
        super().__init__(title="Student authorization", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        input_name = inter.text_values["full_name"].strip().title()
        students = await find_student_by_name(input_name)

        if not students:
            await inter.response.send_message(
                "You are not on the student lists. Please check that you entered your full name correctly",
                ephemeral=True,
            )
            return

        if len(students) > 1:
            await inter.response.send_message(
                "Multiple students with this full name were found. Please contact an administrator.",
                ephemeral=True,
            )
            return

        student = students[0]

        if student["discord_id"] is not None:
            await inter.response.send_message(
                "This student is already registered in the system", ephemeral=True
            )
            return

        db_success = await register_student(
            student_id=student["student_id"], discord_id=inter.author.id
        )

        if not db_success:
            await inter.response.send_message(
                "Database error during registration", ephemeral=True
            )
            return

        _success, roles_msg = await process_student_verification(
            guild=inter.guild, member=inter.author, full_name=input_name
        )
        await inter.response.send_message(roles_msg, ephemeral=True)

        if _success and inter.guild:
            log_channel = inter.guild.get_channel(int(LOG_CHANNEL_ID))
            if log_channel:
                try:
                    await log_channel.send(
                        f"User {inter.author.mention} (`{inter.author.id}`) "
                        f"was successfully verified as: **{input_name}**"
                    )
                except (disnake.Forbidden, disnake.HTTPException):
                    pass


class RegisterView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Start verification",
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
        name="setup_reg", description="Post the verification block in the channel"
    )
    @commands.has_permissions(administrator=True)
    async def setup_reg(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="Student verification",
            description=(
                "To get access to your faculty roles and channels, "
                "click the button below and enter your full name"
            ),
            color=disnake.Color.green(),
        )
        embed.set_footer(text="Automatic registration system")

        await inter.channel.send(embed=embed, view=RegisterView())
        await inter.response.send_message(
            "Verification block sent successfully", ephemeral=True
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(AuthCog(bot))
