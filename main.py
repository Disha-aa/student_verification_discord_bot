import asyncio
import logging
import os
from pathlib import Path

import disnake
from db.database import close_db_pool, init_db
from disnake.ext import commands
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("BOT_TOKEN")
SERVER_ID = int(os.getenv("DISCORD_SERVER_ID").strip())

intents = disnake.Intents.default()
intents.members = True

bot = commands.InteractionBot(
    intents=intents,
    test_guilds=[SERVER_ID],
    command_sync_flags=commands.CommandSyncFlags.all(),
)

bot.load_extension("cogs.auth")
bot.load_extension("cogs.admin")


@bot.event
async def on_ready():
    logging.info(f"Bot started successfully as {bot.user} (ID: {bot.user.id})")


async def main():
    await init_db()
    try:
        await bot.start(TOKEN)
    finally:
        await close_db_pool()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
