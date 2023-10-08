import sqlite3
import bcrypt
from tkinter import messagebox

# Создаем базу данных SQLite и таблицу для хранения данных пользователей
connection = sqlite3.connect("users.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, blocked BOOLEAN)")
connection.commit()
connection.close()

# Создаем таблицу для хранения настроек администратора

connection = sqlite3.connect("users.db")
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_settings (
id INTEGER PRIMARY KEY,
min_length INTEGER,
require_latin BOOLEAN,
require_cyrillic BOOLEAN,
require_arithmetic BOOLEAN,
require_reverse_username BOOLEAN)
    """)
connection.commit()
connection.close()


# Функция для чтения настроек администратора
def load_admin_settings():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM admin_settings LIMIT 1")
    settings = cursor.fetchone()
    connection.close()
    if settings:
        return {
            "min_length": settings[1],
            "require_latin": bool(settings[2]),
            "require_cyrillic": bool(settings[3]),
            "require_arithmetic": bool(settings[4]),
            "require_reverse_username": bool(settings[5])
        }
    else:
        return None

# Функция для сохранения настроек администратора
def save_admin_settings(min_length, require_latin, require_cyrillic, require_arithmetic, require_reverse_username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM admin_settings")
    cursor.execute("INSERT INTO admin_settings (min_length, require_latin, require_cyrillic, require_arithmetic, require_reverse_username) VALUES (?, ?, ?, ?, ?)",
                   (min_length, int(require_latin), int(require_cyrillic), int(require_arithmetic), int(require_reverse_username)))
    connection.commit()
    connection.close()


# Функция для хэширования пароля
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Функция для проверки учетных данных
def check_credentials(username, password):
    # Подключаемся к базе данных
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Ищем пользователя по имени
    cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[1]
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return True
    return False

# Функция для регистрации нового пользователя
def register_user(new_username, new_password):
    # Подключаемся к базе данных
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Проверяем, не существует ли пользователь с таким именем
    cursor.execute("SELECT username FROM users WHERE username=?", (new_username,))
    existing_user = cursor.fetchone()

    if existing_user:
        return False
    else:
        # Хэшируем пароль перед сохранением
        hashed_password = hash_password(new_password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, hashed_password))
        connection.commit()
        return True

# Функция для изменения пароля пользователя
def change_user_password(username, old_password, new_password):
    # Подключаемся к базе данных
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Ищем пользователя по имени
    cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[1]
        # Проверяем хэш старого пароля
        if bcrypt.checkpw(old_password.encode('utf-8'), stored_password):
            # Хэшируем новый пароль перед сохранением
            new_hashed_password = hash_password(new_password)
            cursor.execute("UPDATE users SET password=? WHERE username=?", (new_hashed_password, username))
            connection.commit()
            connection.close()
            return True

    connection.close()
    return False


# Функция для проверки сложности пароля
def is_password_strong(password, username):
    # Извлекаем настройки сложности пароля из базы данных
    admin_settings = load_admin_settings()

    if admin_settings:
        min_length = admin_settings["min_length"]
        require_latin = admin_settings["require_latin"]
        require_cyrillic = admin_settings["require_cyrillic"]
        require_arithmetic = admin_settings["require_arithmetic"]
        require_reverse_username = admin_settings["require_reverse_username"]

        # Проверяем минимальную длину пароля
        if len(password) < min_length:
            return False

        # Проверяем наличие латинских букв
        if require_latin and not any(char.isalpha() and char.isascii() for char in password):
            return False

        # Проверяем наличие кириллических символов
        if require_cyrillic and not any(char.isalpha() and not char.isascii() for char in password):
            return False

        # Проверяем наличие знаков арифметических операций
        if require_arithmetic and not any(char in "+-*/" for char in password):
            return False

        # Проверяем отсутствие совпадения с именем пользователя в обратном порядке
        if require_reverse_username and password == username[::-1]:
            return False

    return True


def block_user(username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET blocked = 1 WHERE username = ?", (username,))
    connection.commit()
    connection.close()

def unblock_user(username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET blocked = 0 WHERE username = ?", (username,))
    connection.commit()
    connection.close()


def load_users():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT username, blocked FROM users")
    users = cursor.fetchall()
    connection.close()
    return users


def get_user_info(username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT username, blocked FROM users WHERE username = ?", (username,))
    user_info = cursor.fetchone()
    connection.close()

    if user_info:
        username, blocked = user_info
        return {"username": username, "blocked": bool(blocked)}
    else:
        return None
