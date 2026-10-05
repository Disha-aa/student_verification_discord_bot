# Student Verification Discord Bot

A Discord bot that checks students against a list and gives them roles.

You load your student list into the database. People on your server click a button, type their full name, and if they're on the list the bot gives them a "verified" role plus the role for their group.

Built with disnake, asyncpg and PostgreSQL. Runs in Docker Compose.

---

## How it works

1. On the first start the bot fills the database from two files: `fill_database/group.csv` (the students) and `fill_database/roles_config.json` (which Discord role belongs to which group).
2. An administrator runs `/setup_reg` in a channel, and the bot posts a message with a verification button.
3. A user clicks the button and enters their full name.
4. The bot looks the name up. Case and extra spaces at the start or end don't matter. If there's exactly one match and nobody has claimed it yet, the bot links that record to the user's Discord account and gives them the verified role and their group role.
5. If Discord doesn't let the bot give the roles (missing permissions or the bot's role is too low), the link is undone so the user can try again later.
6. Every successful verification is posted to a log channel.

All replies to users are only visible to them, so nobody else in the channel sees the names.

---

## Features

- The verification button keeps working after the bot restarts
- English and Ukrainian interface, switched with one setting
- Admin commands for manual verification, unverifying and removing users
- Log channel for verifications and admin actions

---

## Commands

| Command | Who can use it | What it does |
| :--- | :--- | :--- |
| `/setup_reg` | Server administrators | Posts the verification message in the current channel |
| `/verification_user` | Admins | Verifies a member by hand: adds them to the database with the name and group you give (groups 1–9) and gives the roles |
| `/unverify_user` | Admins | Unlinks a member from their record and takes the roles away. The record stays, so they can verify again |
| `/delete_user` | Admins | Deletes the member's record from the database and takes the roles away |
| `/grant_admin` | Owners | Makes a verified member an admin of the bot |

Admins are people with the Administrator permission on the server, plus anyone marked as `admin` or `owner` in the bot's database.
Owners are the server owner, plus the people listed in `OWNERS`.

---

## Tech stack

- Python 3.12
- disnake
- asyncpg
- PostgreSQL 16
- Docker Compose

---

## Setup

### What you need

- Docker with Docker Compose v2
- A Discord application with a bot. In the [Developer Portal](https://discord.com/developers/applications) turn on **Server Members Intent**. No other privileged intents are needed.
- Invite the bot with the `bot` and `applications.commands` scopes and the **Manage Roles** permission. In the server's role list, the bot's role has to be above the roles it gives out.
- Developer Mode in Discord (Settings → Advanced) so you can copy server, channel and role IDs.

### 1. Clone and fill in `.env`

```bash
git clone https://github.com/Disha-aa/student_verification_discord_bot.git
cd student_verification_discord_bot
cp .env.example .env
```

Open `.env` and fill it in:

```bash
BOT_TOKEN=your_bot_token_here
BOT_LANGUAGE=en
DISCORD_SERVER_ID=123456789012345678
VERIFIED_ROLE_ID=123456789012345678
LOG_CHANNEL_ID=123456789012345678
OWNERS=Morgan Liam

POSTGRES_DB=bot_db
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_PORT=5432
POSTGRES_HOST=postgres

DATABASE_URL=postgresql://bot_user:secure_password_here@postgres:5432/bot_db
```

What each one means:

- `BOT_TOKEN` is your bot's token.
- `BOT_LANGUAGE` is `en` or `uk`. If you leave it out, the bot uses Ukrainian.
- `DISCORD_SERVER_ID` is the server the bot works on. Slash commands are registered there.
- `VERIFIED_ROLE_ID` is the role everyone gets after passing verification.
- `LOG_CHANNEL_ID` is where the bot posts verification logs.
- `OWNERS` is a comma-separated list of full names. Write them exactly as they'd look from the CSV: last name, first name, patronymic. These people get the `owner` role in the bot's database when it's first filled.
- `POSTGRES_*` set up the database container. `POSTGRES_PORT` is the port the database is available on from your machine.
- `DATABASE_URL` is how the bot connects to the database. Use the same user, password and database name as above. The host stays `postgres`, which is the name of the database service in `docker-compose.yml`.

### 2. Add your students and roles

```bash
cp fill_database/group.example.csv fill_database/group.csv
cp fill_database/roles_config.example.json fill_database/roles_config.json
```

In `roles_config.json`, map each group number to a Discord role ID:

```json
{
  "1": 100000000000000001,
  "2": 100000000000000002,
  "3": 100000000000000003
}
```

In `group.csv`, put one student per line, without a header:

```csv
Carter,Oliver,,1
Bennett,Sophia,,1
Fletcher,Noah,,2
```

The columns are:

1. Last name
2. First name
3. Patronymic (can be empty)
4. Group number (has to exist in `roles_config.json`)

Lines that don't fit this format are skipped.

### 3. Start it

```bash
docker compose up -d --build
```

To see what the bot is doing:

```bash
docker compose logs -f bot
```

---

## Good to know

The database is filled from `group.csv` and `roles_config.json` only once, when the students table is still empty. If you edit those files later, the bot won't pick up the changes on its own.

If you want to start over and reload everything from the files, delete the database volume:

```bash
docker compose down -v
docker compose up -d --build
```

This wipes all data, including who has already verified.

---

## Project structure

```text
main.py                  starts the bot
cogs/auth.py             verification button and modal, /setup_reg
cogs/admin.py            admin commands
services/verification.py giving and removing roles
db/database.py           database queries
db/schema.sql            tables
fill_database/fill_db.py loads students and owners into the database
utils/security.py        admin and owner checks
utils/i18n.py            English and Ukrainian texts
```