import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

_pool = None

BASE_PATH = Path(__file__).resolve().parent

SCHEMA_PATH = BASE_PATH / "schema.sql"


async def init_db_pool():
    global _pool
    if not DATABASE_URL:
        raise ValueError("pool error")

    _pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=2, max_size=10)


async def close_db_pool():
    if _pool:
        await _pool.close()


def load_schema() -> str:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    return schema_sql


@asynccontextmanager
async def get_connections() -> AsyncGenerator[asyncpg.Connection, None]:
    if _pool is None:
        raise RuntimeError("conn pool error")

    async with _pool.acquire() as conn:
        yield conn


async def is_db_empty(conn) -> bool:
    val = await conn.fetchval("SELECT 1 FROM students LIMIT 1;")
    return val is None


async def init_db():
    if _pool is None:
        await init_db_pool()

    if not SCHEMA_PATH.exists():
        logging.error("Database schema file schema.sql not found!")
        return

    schema_sql = load_schema()

    async with get_connections() as conn:
        await conn.execute(schema_sql)

        if await is_db_empty(conn):
            from fill_database.fill_db import (
                load_roles_config,
                load_students_in_db,
            )

            groups = load_roles_config()
            await add_group_role_id(groups)
            await load_students_in_db()

    logging.info("Database schema initialized and verified.")


async def add_group_role_id(groups: dict[int, int]):
    async with get_connections() as conn:
        await conn.executemany(
            """
            INSERT INTO nure_groups (group_number, discord_role_id)
            VALUES ($1, $2)
            ON CONFLICT (group_number) 
            DO UPDATE SET discord_role_id = EXCLUDED.discord_role_id;
            """,
            groups.items(),
        )


async def add_student(
    full_name: str, user_group: int, discord_id: int | None = None
) -> bool:
    normalized_name = full_name.strip().lower()

    try:
        async with get_connections() as conn:
            status = await conn.execute(
                "INSERT INTO students (full_name, normalized_name, user_group, discord_id)  VALUES ($1, $2, $3, $4)",
                full_name,
                normalized_name,
                user_group,
                discord_id,
            )
            return status == "INSERT 0 1"

    except asyncpg.UniqueViolationError:
        return False


async def set_owner_role(user_owner: str) -> bool:
    try:
        async with get_connections() as conn:
            status = await conn.execute(
                "UPDATE students SET user_role = $1 WHERE full_name = $2",
                "owner",
                user_owner,
            )
            return status == "UPDATE 1"

    except asyncpg.UniqueViolationError:
        return False


async def find_student_by_name(input_name: str) -> list[dict]:
    normalized_name = input_name.strip().lower()

    async with get_connections() as conn:
        rows = await conn.fetch(
            "SELECT * FROM students WHERE normalized_name = $1",
            normalized_name,
        )
        return [dict(row) for row in rows]


async def get_discord_id_role(input_name: str) -> int | None:
    normalized_name = input_name.strip().lower()

    async with get_connections() as conn:
        return await conn.fetchval(
            """
            SELECT g.discord_role_id 
            FROM nure_groups g 
            INNER JOIN students s
            ON g.group_number = s.user_group
            WHERE s.normalized_name = $1
            LIMIT 1
            """,
            normalized_name,
        )


async def register_student(student_id: int, discord_id: int) -> bool:
    try:
        async with get_connections() as conn:
            status = await conn.execute(
                "UPDATE students SET discord_id = $1, registered_at = CURRENT_TIMESTAMP WHERE student_id = $2",
                discord_id,
                student_id,
            )
            return status == "UPDATE 1"

    except asyncpg.UniqueViolationError:
        return False


async def get_student_by_discord_id(discord_id: int) -> dict | None:
    async with get_connections() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM students WHERE discord_id = $1",
            discord_id,
        )
        return dict(row) if row else None


async def update_student_role(discord_id: int, new_role: str) -> bool:
    async with get_connections() as conn:
        status = await conn.execute(
            "UPDATE students SET user_role = $1 WHERE discord_id = $2",
            new_role,
            discord_id,
        )
        return status == "UPDATE 1"


async def unverify_student(discord_id: int) -> bool:
    async with get_connections() as conn:
        status = await conn.execute(
            "UPDATE students SET discord_id = NULL, registered_at = NULL WHERE discord_id = $1",
            discord_id,
        )
        return status == "UPDATE 1"


async def delete_user_from_db(discord_id: int) -> bool:
    async with get_connections() as conn:
        status = await conn.execute(
            "DELETE FROM students WHERE discord_id = $1",
            discord_id,
        )
        return status == "DELETE 1"


async def get_role_id_by_discord_id(discord_id: int) -> int | None:
    async with get_connections() as conn:
        return await conn.fetchval(
            """
            SELECT g.discord_role_id
            FROM nure_groups g
            INNER JOIN students s ON g.group_number = s.user_group
            WHERE s.discord_id = $1
            LIMIT 1;
            """,
            discord_id,
        )
