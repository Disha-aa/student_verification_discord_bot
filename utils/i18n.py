import os

DEFAULT_LANGUAGE = "uk"

raw_lang = os.getenv("BOT_LANGUAGE", DEFAULT_LANGUAGE).strip().lower()
if raw_lang in ("ua", "uk", "ukrainian"):
    CURRENT_LANGUAGE = "uk"
else:
    CURRENT_LANGUAGE = "en"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "uk": {
        "modal_title": "Авторизація студента",
        "modal_name_label": "Введіть ваше ПІБ (українською)",
        "modal_name_placeholder": "Шевченко Тарас Григорович",
        "not_in_lists": "Вас немає в списках студентів. Перевірте правильність введення ПІБ",
        "multiple_found": "Знайдено декількох студентів з таким ПІБ. Зверніться до адміністратора.",
        "already_registered": "Цей студент вже зареєстрований у системі",
        "db_error_register": "Помилка бази даних при реєстрації",
        "log_verified": "Користувач {member} (`{member_id}`) успішно верифікований як: **{name}**",
        "btn_verify": "Пройти верифікацію",
        "setup_reg_desc": "Надіслати блок верифікації в канал",
        "embed_title": "Верифікація студентів",
        "embed_desc": (
            "Щоб отримати доступ до ролей та каналів факультету, "
            "натисніть кнопку нижче та введіть своє повне ПІБ"
        ),
        "embed_footer": "Система автоматичної реєстрації",
        "setup_reg_success": "Блок успішно надіслано",
        "group_not_found": "Не знайдено групу для вказаного студента",
        "roles_granted": "Ролі успішно надано!",
        "roles_empty": "Список ролей для видачі порожній",
        "bot_no_perms": "У бота недостатньо прав для видачі ролей (перевірте ієрархію ролей)",
        "api_error": "Помилка Discord API при призначенні ролей",
        "guild_not_found": "Помилка: сервер не знайдено",
        "role_reason": "Успішна верифікація ПІБ",
        "unverify_reason": "Скасовано верифікацію адміністратором {author}",
        "only_owner": "Команда доступна тільки для Owner!",
        "only_admin": "Команда доступна тільки для адміна!",
        "grant_admin_desc": "Надати права адміна користувачу",
        "not_verified_yet": "{member} ще не пройшов верифікацію",
        "already_has_admin": "{member} вже має роль адміна",
        "db_role_update_failed": "Не вдалося оновити роль в базі даних",
        "grant_admin_success": "Користувачу {member} успішно надано роль **admin** в базі даних!",
        "verify_user_desc": "Вручну верифікувати студента",
        "invalid_group": "У нас всього 9 груп",
        "enter_full_name": "Введіть повне ПІБ",
        "user_already_verified": "{member} вже пройшов верифікацію",
        "db_insert_error": "Помилка в базі даних: не вдалося додати запис",
        "manual_verify_role_err": "Запис створено, але сталася помилка з ролями: {error}",
        "manual_verify_success": "Студента {name} успішно прив'язано до {member}, ролі надано",
        "log_manual_verify": "Адміністратор {author} вручну верифікував користувача {member} (`{member_id}`) як: **{name}** | Група: **{group}**",
        "unverify_desc": "Скасувати верифікацію користувача",
        "user_not_found_db": "Користувача {member} не знайдено в базі даних",
        "unverify_role_err": "У користувача {member} скасована верифікація в БД, але роль зняти не вдалося (перевірте права)",
        "unverify_success": "У {member} успішно скасована верифікація",
        "log_unverify": "Адміністратор {author} скасував верифікацію користувача {member} (`{member_id}`)",
        "delete_user_desc": "Видалити користувача з бази даних",
        "delete_role_err": "Користувача {member} видалено з бази даних, але роль зняти не вдалося",
        "delete_success": "Користувача {member} успішно видалено з бази даних",
        "log_delete": "Адміністратор {author} видалив з бази даних користувача {member} (`{member_id}`)",
        "reg_rollback_msg": "Сталася помилка при видачі ролей Discord ({error}). Спробуйте ще раз або зверніться до адміністратора."
    },
    "en": {
        "modal_title": "Student Authorization",
        "modal_name_label": "Enter your full name",
        "modal_name_placeholder": "Last name First name Patronymic",
        "not_in_lists": "You are not on the student lists. Please check that you entered your full name correctly",
        "multiple_found": "Multiple students with this full name were found. Please contact an administrator.",
        "already_registered": "This student is already registered in the system",
        "db_error_register": "Database error during registration",
        "log_verified": "User {member} (`{member_id}`) successfully verified as: **{name}**",
        "btn_verify": "Start verification",
        "setup_reg_desc": "Post the verification block in the channel",
        "embed_title": "Student Verification",
        "embed_desc": (
            "To get access to your faculty roles and channels, "
            "click the button below and enter your full name"
        ),
        "embed_footer": "Automatic registration system",
        "setup_reg_success": "Verification block sent successfully",
        "group_not_found": "Group not found for specified student",
        "roles_granted": "Roles granted successfully!",
        "roles_empty": "Role list is empty",
        "bot_no_perms": "Bot does not have permissions to manage roles (check role hierarchy)",
        "api_error": "Discord API error when granting roles",
        "guild_not_found": "Error: server not found",
        "role_reason": "Successful student verification",
        "unverify_reason": "Unverified by administrator {author}",
        "only_owner": "This command is only available to the Owner!",
        "only_admin": "This command is only available to an administrator!",
        "grant_admin_desc": "Grant admin permissions to a user",
        "not_verified_yet": "{member} has not completed verification yet",
        "already_has_admin": "{member} already has the admin role",
        "db_role_update_failed": "Failed to update role in the database",
        "grant_admin_success": "User {member} was successfully granted the **admin** role in the database!",
        "verify_user_desc": "Manually verify a student",
        "invalid_group": "We only have 9 groups",
        "enter_full_name": "Please enter full name",
        "user_already_verified": "{member} has already completed verification",
        "db_insert_error": "Database error: failed to add record",
        "manual_verify_role_err": "Record created, but an error occurred with roles: {error}",
        "manual_verify_success": "Student {name} successfully linked to {member}, roles granted",
        "log_manual_verify": "Administrator {author} manually verified user {member} (`{member_id}`) as: **{name}** | Group: **{group}**",
        "unverify_desc": "Cancel user verification",
        "user_not_found_db": "User {member} not found in database",
        "unverify_role_err": "User {member} was unverified in DB, but failed to remove role (check permissions)",
        "unverify_success": "Verification successfully cancelled for {member}",
        "log_unverify": "Administrator {author} cancelled verification for {member} (`{member_id}`)",
        "delete_user_desc": "Delete user from database",
        "delete_role_err": "User {member} was deleted from DB, but failed to remove role",
        "delete_success": "User {member} was successfully deleted from database",
        "log_delete": "Administrator {author} deleted user {member} (`{member_id}`) from database",
        "reg_rollback_msg": "An error occurred while granting Discord roles ({error}). Please try again or contact an administrator."
    }
}


def t(key: str, **kwargs) -> str:
    lang_dict = TRANSLATIONS.get(CURRENT_LANGUAGE, TRANSLATIONS[DEFAULT_LANGUAGE])
    text = lang_dict.get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
