import tkinter as tk
from tkinter import messagebox
import logic
import sqlite3
from tkinter import messagebox
import psutil  # Импортируем библиотеку psutil для получения информации о системе


# Функция для сохранения сигнатуры компьютера в базу данных
def save_computer_signature():
    username = username_entry.get()

    try:
        # Получаем данные о системе
        computer_info = {
            "username": psutil.users()[0].name,  # Имя пользователя системы
            "computer_name": psutil.users()[0].terminal,  # Имя компьютера
            "os_path": psutil.disk_partitions()[0].device,  # Путь к папке с ОС Windows
            "screen_width": tk.Tk().winfo_screenwidth(),  # Ширина экрана
            "screen_height": tk.Tk().winfo_screenheight(),  # Высота экрана
            "ram_info": psutil.virtual_memory().total,  # Объем ОЗУ
            "hdd_info": psutil.disk_usage('/').total,  # Объем HDD
            "hdd_label": psutil.disk_partitions()[0].fstype  # Метка типа файловой системы HDD
        }

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        # Создаем таблицу, если она не существует
        cursor.execute('''CREATE TABLE IF NOT EXISTS computer_signature (
            id INTEGER PRIMARY KEY,
            username TEXT,
            computer_name TEXT,
            os_path TEXT,
            screen_width INTEGER,
            screen_height INTEGER,
            ram_info INTEGER,
            hdd_info INTEGER,
            hdd_label TEXT
        )''')

        # Пытаемся вставить данные в таблицу
        cursor.execute('''INSERT INTO computer_signature (
            username, computer_name, os_path, screen_width, screen_height, ram_info, hdd_info, hdd_label
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (computer_info["username"], computer_info["computer_name"], computer_info["os_path"],
                        computer_info["screen_width"], computer_info["screen_height"], computer_info["ram_info"],
                        computer_info["hdd_info"], computer_info["hdd_label"]))

        connection.commit()
        connection.close()

        messagebox.showinfo("Сигнатура компьютера", "Сигнатура компьютера успешно сохранена!")

    except Exception as e:
        print("Error saving computer signature:", str(e))
        messagebox.showerror("Ошибка", "Не удалось сохранить сигнатуру компьютера.")


# Функция для проверки сигнатуры компьютера
def check_computer_signature():
    try:
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        # Получаем последнюю сохраненную сигнатуру компьютера
        cursor.execute("SELECT * FROM computer_signature ORDER BY id DESC LIMIT 1")
        saved_signature = cursor.fetchone()

        if saved_signature:
            # Получаем текущие данные о системе
            computer_info = {
                "username": psutil.users()[0].name,
                "computer_name": psutil.users()[0].terminal,
                "os_path": psutil.disk_partitions()[0].device,
                "screen_width": tk.Tk().winfo_screenwidth(),
                "screen_height": tk.Tk().winfo_screenheight(),
                "ram_info": psutil.virtual_memory().total,
                "hdd_info": psutil.disk_usage('/').total,
                "hdd_label": psutil.disk_partitions()[0].fstype
            }

            # Сравниваем текущую сигнатуру с сохраненной
            if (
                    computer_info["username"] != saved_signature[1] or
                    computer_info["computer_name"] != saved_signature[2] or
                    computer_info["os_path"] != saved_signature[3] or
                    computer_info["screen_width"] != saved_signature[4] or
                    computer_info["screen_height"] != saved_signature[5] or
                    computer_info["ram_info"] != saved_signature[6] or
                    computer_info["hdd_info"] != saved_signature[7] or
                    computer_info["hdd_label"] != saved_signature[8]
            ):
                messagebox.showerror("Ошибка сигнатуры компьютера",
                                     "Сигнатура компьютера не совпадает. Программа завершена.")
                root.quit()

        connection.close()

    except Exception as e:
        print("Error checking computer signature:", str(e))
        messagebox.showerror("Ошибка", "Не удалось проверить сигнатуру компьютера.")


# Глобальный счетчик попыток
login_attempts = 0

# Максимальное количество попыток
MAX_ATTEMPTS = 3

# Функция для успешной авторизации
def successful_login(username):
    global main_window
    main_window = tk.Toplevel(root)
    main_window.title("Главное окно")
    main_window.geometry("400x200")

    welcome_label = tk.Label(main_window, text="Добро пожаловать, " + username + "!")
    welcome_label.pack()

    logout_button = tk.Button(main_window, text="Выйти", command=main_window.destroy)
    logout_button.pack()

    # Добавляем кнопку "Сменить пароль"
    change_password_button = tk.Button(main_window, text="Сменить пароль", command=change_password)
    change_password_button.pack()



# Функция для смены пароля
def change_password():
    global change_password_window
    change_password_window = tk.Toplevel(main_window)
    change_password_window.title("Смена пароля")
    change_password_window.geometry("400x150")

    # Создаем и размещаем элементы интерфейса для смены пароля
    old_password_label = tk.Label(change_password_window, text="Старый пароль:")
    old_password_label.pack()
    old_password_entry = tk.Entry(change_password_window, show="*")
    old_password_entry.pack()

    new_password_label = tk.Label(change_password_window, text="Новый пароль:")
    new_password_label.pack()
    new_password_entry = tk.Entry(change_password_window, show="*")
    new_password_entry.pack()

    change_button = tk.Button(change_password_window, text="Сменить пароль", command=lambda: change_user_password(old_password_entry.get(), new_password_entry.get()))
    change_button.pack()


# Функция для смены пароля пользователя
def change_user_password(old_password, new_password):
    username = username_entry.get()
    if logic.change_user_password(username, old_password, new_password):
        messagebox.showinfo("Смена пароля", "Пароль успешно изменен")
        change_password_window.destroy()
    else:
        messagebox.showerror("Ошибка смены пароля", "Не удалось изменить пароль. Проверьте старый пароль.")

# Функция для открытия окна панели администратора
def open_admin_panel():
    global admin_window
    admin_window = tk.Toplevel(root)
    admin_window.title("Панель администратора")
    admin_window.geometry("400x200")

    admin_label = tk.Label(admin_window, text="Вы вошли как администратор!")
    admin_label.pack()

    # Добавляем кнопку "Выйти из админ-панели"
    admin_logout_button = tk.Button(admin_window, text="Выйти", command=admin_window.destroy)
    admin_logout_button.pack()

    # Добавляем кнопку "Сменить пароль"
    change_password_button = tk.Button(admin_window, text="Сменить пароль", command=change_password)
    change_password_button.pack()

    # Добавляем кнопку "Просмотреть пользователей"
    view_users_button = tk.Button(admin_window, text="Просмотреть пользователей", command=view_users)
    view_users_button.pack()

    settingsPass_button = tk.Button(admin_window, text="Настройки паролей", command=open_admin_settings)
    settingsPass_button.pack()

# Функция для авторизации пользователя и проверки сигнатуры компьютера
def login_with_signature_check():
    global login_attempts
    username = username_entry.get()
    password = password_entry.get()

    user_info = logic.get_user_info(username)

    if user_info and user_info["blocked"]:
        messagebox.showerror("Ошибка авторизации", "Учетная запись заблокирована. Обратитесь к администратору.")
        return

    if logic.check_credentials(username, password):
        check_computer_signature()  # Проверяем сигнатуру компьютера
        messagebox.showinfo("Успешная авторизация", "Авторизация прошла успешно!")
        if username == "admin":
            open_admin_panel()
        else:
            successful_login(username)
    else:
        login_attempts += 1
        if login_attempts >= MAX_ATTEMPTS:
            messagebox.showerror("Ошибка авторизации", "Превышено количество попыток. Программа завершена.")
            root.quit()
        else:
            messagebox.showerror("Ошибка авторизации", "Неверное имя пользователя или пароль. Попробуйте еще раз.")

# Функция для регистрации нового пользователя
def register_user():
    new_username = new_username_entry.get()
    new_password = new_password_entry.get()

    if not new_username or not new_password:
        messagebox.showerror("Ошибка регистрации", "Введите имя пользователя и пароль")
        return

    if not logic.is_password_strong(new_password, new_username):
        messagebox.showerror("Ошибка регистрации", "Пароль не удовлетворяет требованиям сложности")
        return

    if logic.register_user(new_username, new_password):
        messagebox.showinfo("Успешная регистрация", "Регистрация прошла успешно!")
    else:
        messagebox.showerror("Ошибка регистрации", "Пользователь с таким именем уже существует")


def view_users():
    global view_users_window
    view_users_window = tk.Toplevel(admin_window)
    view_users_window.title("Зарегистрированные пользователи")
    view_users_window.geometry("400x300")

    def update_user_list():
        users_listbox.delete(0, tk.END)
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("SELECT username, blocked FROM users")
        users = cursor.fetchall()
        connection.close()
        for user, blocked in users:
            status = "Заблокирован" if blocked else "Активен"
            users_listbox.insert(tk.END, f"{user} ({status})")

    # Подключаемся к базе данных
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Получаем список зарегистрированных пользователей с информацией о блокировке
    cursor.execute("SELECT username, blocked FROM users")
    users = cursor.fetchall()

    # Создаем и размещаем элементы интерфейса для отображения пользователей и их статуса блокировки
    users_label = tk.Label(view_users_window, text="Зарегистрированные пользователи:")
    users_label.pack()

    users_listbox = tk.Listbox(view_users_window, selectmode=tk.SINGLE)
    for user, blocked in users:
        status = "Заблокирован" if blocked else "Активен"
        users_listbox.insert(tk.END, f"{user} ({status})")
    users_listbox.pack()

    def block_user():
        selected_user = users_listbox.get(tk.ACTIVE)
        username = selected_user.split(" ")[0]
        logic.block_user(username)
        update_user_list()

    def unblock_user():
        selected_user = users_listbox.get(tk.ACTIVE)
        username = selected_user.split(" ")[0]
        logic.unblock_user(username)
        update_user_list()

    block_button = tk.Button(view_users_window, text="Заблокировать", command=block_user)
    block_button.pack()

    unblock_button = tk.Button(view_users_window, text="Разблокировать", command=unblock_user)
    unblock_button.pack()

    admin_logout_button = tk.Button(view_users_window, text="Выйти", command=view_users_window.destroy)
    admin_logout_button.pack()

    # Закрываем соединение с базой данных
    connection.close()

# Функция для открытия окна настроек администратора
def open_admin_settings():
    global admin_settings_window
    admin_settings_window = tk.Toplevel(admin_window)
    admin_settings_window.title("Настройки администратора")
    admin_settings_window.geometry("400x200")

    # Создаем и размещаем элементы интерфейса для настройки требований
    min_length_label = tk.Label(admin_settings_window, text="Минимальная длина пароля:")
    min_length_label.pack()
    min_length_entry = tk.Entry(admin_settings_window)
    min_length_entry.pack()

    require_latin_var = tk.BooleanVar()
    require_latin_checkbox = tk.Checkbutton(admin_settings_window, text="Требовать латинские буквы", variable=require_latin_var)
    require_latin_checkbox.pack()

    require_cyrillic_var = tk.BooleanVar()
    require_cyrillic_checkbox = tk.Checkbutton(admin_settings_window, text="Требовать кириллические символы", variable=require_cyrillic_var)
    require_cyrillic_checkbox.pack()

    require_arithmetic_var = tk.BooleanVar()
    require_arithmetic_checkbox = tk.Checkbutton(admin_settings_window, text="Требовать знаки арифметических операций", variable=require_arithmetic_var)
    require_arithmetic_checkbox.pack()

    require_reverse_username_var = tk.BooleanVar()
    require_reverse_username_checkbox = tk.Checkbutton(admin_settings_window, text="Требовать несовпадение с именем пользователя в обратном порядке", variable=require_reverse_username_var)
    require_reverse_username_checkbox.pack()

    save_button = tk.Button(admin_settings_window, text="Сохранить", command=lambda: logic.save_admin_settings(min_length_entry.get(),
                                                                                                    require_latin_var.get(),
                                                                                                    require_cyrillic_var.get(),
                                                                                                    require_arithmetic_var.get(),
                                                                                                    require_reverse_username_var.get()))
    save_button.pack()

    # Загрузка текущих настроек из базы данных (если они существуют)
    admin_settings = logic.load_admin_settings()
    if admin_settings:
        min_length_entry.insert(0, str(admin_settings["min_length"]))
        require_latin_var.set(admin_settings["require_latin"])
        require_cyrillic_var.set(admin_settings["require_cyrillic"])
        require_arithmetic_var.set(admin_settings["require_arithmetic"])
        require_reverse_username_var.set(admin_settings["require_reverse_username"])



def about_program():
    about_window = tk.Toplevel(root)
    about_window.title("О программе")
    about_window.geometry("300x150")

    about_label = tk.Label(about_window, text="Автор: [Мухин Павел ИСБ-120]\nИндивидуальное задание: [ЛР-1 П/Г-2]")
    about_label.pack()





# Создаем главное окно
root = tk.Tk()
root.title("Окно авторизации")
root.geometry("400x300")

# Создаем и размещаем элементы интерфейса
username_label = tk.Label(root, text="Имя пользователя:")
username_label.pack()
username_entry = tk.Entry(root, width=30)
username_entry.pack()

password_label = tk.Label(root, text="Пароль:")
password_label.pack()
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack()

login_button = tk.Button(root, text="Войти", command=login_with_signature_check)
login_button.pack()

about_button = tk.Button(root, text="О программе", command=about_program)
about_button.pack()

# Создаем и размещаем элементы интерфейса для регистрации
register_label = tk.Label(root, text="Регистрация нового пользователя:")
register_label.pack()

new_username_label = tk.Label(root, text="Имя пользователя:")
new_username_label.pack()
new_username_entry = tk.Entry(root, width=30)
new_username_entry.pack()

new_password_label = tk.Label(root, text="Пароль:")
new_password_label.pack()
new_password_entry = tk.Entry(root, show="*", width=30)
new_password_entry.pack()

register_button = tk.Button(root, text="Зарегистрироваться", command=register_user)
register_button.pack()

logout_button = tk.Button(root, text="Выйти", command=root.destroy)
logout_button.pack()

# Запускаем главный цикл обработки событий
root.mainloop()



