import os
import telebot
import sqlite3
from datetime import datetime

API_TOKEN = os.getenv("7536673665:AAGURJv216qotPw428s_oSo7M4VHoQGY_DA")
bot = telebot.TeleBot(API_TOKEN)


# Список ID администраторов
admin_ids = ["5768048465", "171846439"]

# Подключаемся к SQLite
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу пользователей
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Обычный'
)
""")
conn.commit()


# ✅ /start – Приветственное сообщение
@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

    bot.send_message(user_id, "👋 Привет! Добро пожаловать в программу лояльности!\n"
                              "Вы можете накапливать баллы, участвовать в акциях и обменивать их на бонусы.\n\n"
                              "💡 Используйте /help для списка команд.")


# ✅ /help – Список всех команд
@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(message.from_user.id, "📋 Список команд:\n"
                                           "/start - Информация о программе лояльности\n"
                                           "/status - Проверить ваш текущий статус и баллы\n"
                                           "/rewards - Посмотреть доступные бонусы\n"
                                           "/redeem - Обменять баллы на бонус\n"
                                           "/invite - Пригласить друга\n"
                                           "/feedback - Оставить отзыв\n"
                                           "/events - Посмотреть афишу мероприятий\n"
                                           "/contact - Связаться с администрацией\n"
                                           "/add_points - Начисление баллов (только для администратора)"
                                           "/book_table - Забронировать столик")


# ✅ /status – Проверка баланса и статуса
@bot.message_handler(commands=['status'])
def show_status(message):
    user_id = message.from_user.id
    cursor.execute("SELECT points, status FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        points, status = user
        bot.send_message(user_id, f"💳 Ваш баланс: {points} баллов\n🔹 Ваш статус: {status}")
    else:
        bot.send_message(user_id, "❌ Вы не зарегистрированы. Введите /start.")


# ✅ /rewards – Список бонусов
@bot.message_handler(commands=['rewards'])
def show_rewards(message):
    bot.send_message(message.from_user.id, "🎁 Доступные бонусы:\n"
                                           "1️⃣ Скидка 10% – 250 баллов\n"
                                           "2️⃣ Бесплатный напиток – 400 баллов\n"
                                           "3️⃣ Бесплатный кальян – 1000 баллов")


# ✅ /redeem – Обмен баллов на бонус (уведомление админу)
@bot.message_handler(commands=['redeem'])
def redeem_points(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Введите номер бонуса, который хотите получить:\n"
                              "Пример: /redeem 1 (Скидка 10%)")
    bot.register_next_step_handler(message, process_redeem)


def process_redeem(message):
    user_id = message.from_user.id
    command = message.text.split()

    try:
        reward_id = int(command[1])

        rewards = {1: ("Скидка 10%", 250), 2: ("Бесплатный напиток", 400), 3: ("Бесплатный кальян", 1000)}

        if reward_id in rewards:
            reward_name, cost = rewards[reward_id]

            cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
            points = cursor.fetchone()[0]

            if points >= cost:
                cursor.execute("UPDATE users SET points = points - ? WHERE user_id=?", (cost, user_id))
                conn.commit()
                bot.send_message(user_id, f"✅ Вы успешно обменяли {cost} баллов на '{reward_name}'!")
                for admin_id in admin_ids:
                    bot.send_message(admin_id, f"🔔 Пользователь {user_id} обменял {cost} баллов на '{reward_name}'")
            else:
                bot.send_message(user_id, "❌ Недостаточно баллов!")
        else:
            bot.send_message(user_id, "❌ Неверный номер бонуса!")

    except (IndexError, ValueError):
        bot.send_message(user_id, "⚠ Неправильный формат. Используйте: /redeem <номер_бонуса>")


# ✅ /invite – Пригласить друга
@bot.message_handler(commands=['invite'])
def invite_friend(message):
    bot.send_message(message.from_user.id, "🤝 Пригласите друга по ссылке:\n"
                                           "👉 @BARDUCK_hookah_bar_bot")


# ✅ /feedback – Оставить отзыв
@bot.message_handler(commands=['feedback'])
def feedback(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "📝 Оставьте ваш отзыв или пожелание:")
    bot.register_next_step_handler(message, process_feedback)


def process_feedback(message):
    feedback_text = message.text
    for admin_id in admin_ids:
        bot.send_message(admin_id, f"📢 Новый отзыв:\n{feedback_text}")
    bot.send_message(message.from_user.id, "✅ Спасибо за ваш отзыв!")


# ✅ /events – Афиша мероприятий
@bot.message_handler(commands=['events'])
def show_events(message):
    bot.send_message(message.from_user.id, "🎭 Афиша мероприятий:\n"
                                           "📌 Шеф стол\n"
                                           "📌 Вечер кино\n"
                                           "📌 Трансляция футбола")


# ✅ /contact – Связь с администрацией
@bot.message_handler(commands=['contact'])
def contact_admin(message):
    bot.send_message(message.from_user.id, "☎ Связь с администрацией:\n"
                                           "📞 +998-91-558-86-86\n"
                                           "📲 @saidspc23")


# ✅ /add_points – Начисление баллов админом
@bot.message_handler(commands=['add_points'])
def add_points(message):
    user_id = message.from_user.id

    if str(user_id) in admin_ids:
        try:
            command = message.text.split()
            target_user_id = int(command[1])
            points = int(command[2])

            cursor.execute("SELECT * FROM users WHERE user_id=?", (target_user_id,))
            user = cursor.fetchone()

            if user:
                cursor.execute("UPDATE users SET points = points + ? WHERE user_id=?", (points, target_user_id))
                conn.commit()
                update_status(target_user_id)
                bot.send_message(target_user_id, f"✅ Вам начислено {points} баллов!")
                bot.send_message(user_id, f"Пользователю {target_user_id} успешно начислено {points} баллов.")
            else:
                bot.send_message(user_id, "❌ Пользователь не найден.")
        except (IndexError, ValueError):
            bot.send_message(user_id, "⚠ Неправильный формат. Используйте: /add_points <user_id> <points>")
    else:
        bot.send_message(user_id, "❌ У вас нет прав для использования этой команды.")


# ✅ Функция обновления статуса
def update_status(user_id):
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    new_status = 'Обычный'
    if points >= 10000:
        new_status = 'Золотой'
    elif points >= 5000:
        new_status = 'Серебряный'

    cursor.execute("UPDATE users SET status=? WHERE user_id=?", (new_status, user_id))
    conn.commit()


# ✅ /book_table – Бронирование столика
@bot.message_handler(commands=['book_table'])
def book_table(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "📅 Укажите дату и время для бронирования столика (например, 2025-04-05 19:00(год-месяц-день час-минуты):")
    bot.register_next_step_handler(message, process_booking_date)


def process_booking_date(message):
    user_id = message.from_user.id
    booking_date = message.text.strip()

    try:
        datetime.strptime(booking_date, "%Y-%m-%d %H:%M")

        # Отправляем уведомление обоим администраторам
        for admin_id in admin_ids:
            try:
                bot.send_message(admin_id, f"🔔 Новый запрос на бронирование столика:\n"
                                          f"Пользователь {user_id} забронировал столик на {booking_date}.")
            except Exception as e:
                bot.send_message(user_id, f"❌ Произошла ошибка при отправке уведомления админу {admin_id}: {e}")

        bot.send_message(user_id, f"✅ Ваш столик забронирован на {booking_date}. Мы ждем вас!")

    except ValueError:
        bot.send_message(user_id, "❌ Неверный формат даты и времени. Попробуйте снова (например, 2025-04-05 19:00).")


# ✅ Обработка неверных команд
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "❌ Неверная команда! Введите /help для списка доступных команд.")


# ✅ Запуск бота
bot.polling()