import csv
import json
from pathlib import Path

from db.database import add_student, set_owner_role

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "group.csv"
ROLES_PATH = BASE_DIR / "roles_config.json"

OWNERS = [
    "Morgan Liam",
]


def load_roles_config() -> dict[int, int]:
    if not ROLES_PATH.exists():
        raise FileNotFoundError("not found json")

    with open(ROLES_PATH, "r", encoding="utf-8") as f:
        raw_data: dict[str, int] = json.load(f)

    return {int(group): role_id for group, role_id in raw_data.items()}


def load_student_from_csv():
    if not CSV_PATH.exists():
        return False

    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        lines = csv.reader(f)
        yield from lines

    return True


async def load_students_in_db() -> bool:
    for row in load_student_from_csv():
        if not row or not any(row):
            continue
        try:
            last_name = row[0].strip()
            first_name = row[1].strip()
            patronymic = row[2].strip()
            group_int = int(row[3].strip())
            full_name = f"{last_name} {first_name} {patronymic}"

            await add_student(full_name, group_int)
        except (IndexError, KeyError, ValueError):
            continue

    for user in OWNERS:
        await set_owner_role(user)
    return True
