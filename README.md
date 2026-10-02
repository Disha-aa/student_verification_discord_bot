# Discord Verification Bot

An asynchronous, production-ready Discord bot designed for automated role assignment and member verification based on a pre-seeded database whitelist. Built with **Disnake**, **asyncpg**, and **PostgreSQL 16**, fully containerized via **Docker Compose**.

---

## Architecture Overview

The bot implements a **Pre-seeded Whitelist** security pattern:
1. Server administrators populate the database with eligible members and assigned group identifiers.
2. A user joins the Discord server and interacts with a persistent verification button.
3. A modal dialog collects the user's real name and access group.
4. The service validates the input and atomically associates the user's unique Discord ID with their whitelist record.
5. Upon successful database commitment, the bot updates the member's server nickname and grants corresponding Discord roles.

---

## Key Features

- **Asynchronous I/O Pipeline:** Full end-to-end async implementation leveraging `Disnake` and `asyncpg` connection pooling.
- **Race Condition Protection:** Atomic SQL updates prevent concurrent exploitation of pre-seeded credentials.
- **Persistent UI Engine:** Modal verification views survive bot reboots without losing interaction callbacks.
- **Containerized Infrastructure:** Production-grade `docker-compose` lifecycle management with isolated networks and healthchecks.
- **Strict Data Integrity:** Relational foreign-key enforcement with cascade protection (`ON DELETE RESTRICT`) and `TIMESTAMPTZ` audit trails.

---

## Tech Stack

- **Runtime:** Python 3.14+
- **Discord API Framework:** Disnake
- **Database Driver:** asyncpg
- **Database Engine:** PostgreSQL 16 (Alpine)
- **Containerization:** Docker Compose

---

## Quickstart & Deployment

### 1. Prerequisites
- [Docker Engine](https://docs.docker.com/engine/install/) (v24.0+) & Docker Compose (v2+)
- A registered Discord Application with **Server Members Intent** enabled via the [Discord Developer Portal](https://discord.com/developers/applications).
- Discord **Developer Mode** enabled (Settings -> Advanced -> Developer Mode) to copy Channel, Role, and Server IDs.

---

### 2. Installation & Environment Setup 
Clone the repository and prepare the configuration:

```bash
git clone https://github.com/Disha-aa/student_verification_discord_bot.git
cd student_verification_discord_bot
cp .env.example .env
```
#### Open .env and fill in your credentials:
```bash
BOT_TOKEN=your_bot_token_here
DISCORD_SERVER_ID=123456789012345678
VERIFIED_ROLE_ID=123456789012345678
LOG_CHANNEL_ID=123456789012345678

POSTGRES_DB=bot_db
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_PORT=5432
POSTGRES_HOST=postgres

DATABASE_URL=postgresql://bot_user:secure_password_here@postgres:5432/bot_db
```

## Pre-seeding Configuration

The bot automatically populates the database whitelist on startup. Before launching the containers, you must configure the initial data files from the provided templates.

### Create Data Files
Create your local configuration files from the examples:

```bash
cp group.example.csv group.csv
cp roles_config.example.json roles_config.json
```

#### Configure Role Mappings (roles_config.json)
Define the mapping between numeric access groups and your server's Discord Role Snowflake IDs:
```JSON
{
  "1": 100000000000000001,
  "2": 100000000000000002,
  "3": 100000000000000003
}
```
#### Populate Whitelist (group.csv)
Fill the CSV file with authorized members (no header line):
```CSV
Carter,Oliver,,1
Bennett,Sophia,,1
Fletcher,Noah,,2
```
#### Column layout:

- Last Name (Required) — Participant's surname.
- First Name (Required) — Participant's given name.
- Patronymic / Middle Name (Optional) — Left blank if not applicable.
- Group Number (Required) — Must match an existing key in roles_config.json

#### Administrator Setup (`fill_db.py`)

To automatically grant the elevated server role upon database seeding, define the target names in the `OWNERS` list inside `fill_db.py`:

```python
OWNERS = [
    "Morgan Liam",
]
```

---

### 3. Automatic Ingestion
Once configured, simply start the bot:
```bash
docker compose up -d --build
```
#### On startup, the bot executes the ingestion pipeline automatically:

- Reads and registers group-to-role associations.
- Normalizes participant names and populates the students / whitelist_members table.
- Grants administrative status to configured system owners.