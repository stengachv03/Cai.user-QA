import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import random

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("No BOT_TOKEN environment variable set")

# Replace with actual chat IDs
ADMIN_CHAT_ID = 1075685605  # Chat ID for @sten_anyqx
CREATOR_CHAT_ID = 897127957  # Chat ID for @vl_std

WALLET_ADDRESS = 'TVkXgDHJsMQcR14Mr6uPdpELqJuG6Aok5L'
NETWORK = 'TRC20'

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# In-memory storage for stats and tickets
user_stats = {}  # {user_id: {"messages": int, "ads": int}}
tickets = {}  # {user_id: ticket_id}
next_ticket_id = 1000

# Admin commands
admin_users = {ADMIN_CHAT_ID, CREATOR_CHAT_ID}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_stats[user_id] = user_stats.get(user_id, {"messages": 0, "ads": 0})
    user_stats[user_id]["messages"] += 1
    tickets[user_id] = next_ticket_id
    next_ticket_id += 1

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("💼 Сотрудничество"))
    markup.add(KeyboardButton("💸 Поддержать"))
    markup.add(KeyboardButton("📩 Отправить медиа"))

    welcome_text = (
        "Привет!\n\n"
        "Хочешь задать вопрос? У тебя есть идея для поста/видео? Хочешь разместить рекламу?\n"
        "Или ты хочешь поделиться с сообществом крутым про ИИ ботов?\n"
        "Пиши мне смело 😊\n\n"
        "Я читаю всё с теплом и вниманием 💜"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💸 Поддержать")
def handle_support(message):
    support_text = (
        f"Поддержите нас через USDT via сеть {NETWORK}:\n"
        f"{WALLET_ADDRESS}\n\n"
        "Спасибо за вашу поддержку! 😊"
    )
    bot.send_message(message.chat.id, support_text)

@bot.message_handler(func=lambda message: message.text == "💼 Сотрудничество")
def handle_cooperation(message):
    user_id = message.from_user.id
    user_stats[user_id]["ads"] += 1
    price_list = (
        "💼 Авторазделение по темам: сотрудничество\n\n"
        "Список прайса:\n"
        "1. Ваш пост в одном из тг каналов @characterhh или @janitorai6 - 10$\n"
        "2. Мой обзор и публикация поста о Вашем продукте/канале/приложении в одном из моих каналов - 30$\n"
        "3. Короткий ролик до 10 секунд о Вашем продукте на тик ток аккаунт - 50$\n"
        "4. Разговорный рекламный ролик отзыв о Вашем продукте - 99$\n\n"
        "Все подробности и нюансы обсуждаются лично."
    )
    
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(InlineKeyboardButton("🛒 Хочу заказать рекламу", callback_data="order_ad"))
    
    bot.send_message(message.chat.id, price_list, reply_markup=inline_markup)

@bot.message_handler(func=lambda message: message.text == "📩 Отправить медиа")
def handle_media(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📷 Отправить фото", callback_data="send_photo"))
    markup.add(InlineKeyboardButton("🎥 Отправить видео", callback_data="send_video"))
    bot.send_message(message.chat.id, "Выберите тип медиа:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "order_ad")
def handle_order_ad(call):
    bot.answer_callback_query(call.id)
    greeting = "🛒 Здравствуйте! Мы рады сотрудничать с Вами. Слушаем внимательно Ваше предложение."
    bot.send_message(call.message.chat.id, greeting)
    user_states[call.from_user.id] = 'waiting_proposal'

@bot.callback_query_handler(func=lambda call: call.data in ["send_photo", "send_video"])
def handle_media_request(call):
    user_id = call.from_user.id
    if call.data == "send_photo":
        bot.send_message(user_id, "Пожалуйста, отправьте фото.")
        user_states[user_id] = 'waiting_photo'
    else:
        bot.send_message(user_id, "Пожалуйста, отправьте видео.")
        user_states[user_id] = 'waiting_video'

@bot.message_handler(content_types=['photo', 'video'])
def handle_media_upload(message):
    user_id = message.from_user.id
    if user_id in user_states:
        if user_states[user_id] == 'waiting_photo' and message.content_type == 'photo':
            bot.forward_message(CREATOR_CHAT_ID, message.chat.id, message.message_id)
            bot.send_message(user_id, "Фото отправлено создателю!")
            del user_states[user_id]
        elif user_states[user_id] == 'waiting_video' and message.content_type == 'video':
            bot.forward_message(CREATOR_CHAT_ID, message.chat.id, message.message_id)
            bot.send_message(user_id, "Видео отправлено создателю!")
            del user_states[user_id]
        else:
            bot.send_message(user_id, "Неверный тип медиа. Попробуйте снова.")
    else:
        bot.send_message(user_id, "Отправьте медиа через меню 📩 Отправить медиа.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    text = message.text or "Без текста"
    
    # Auto-tags
    tag = "💡 Вопрос / идея"
    if any(keyword in text.lower() for keyword in ["реклама", "купить", "разместить"]):
        tag = "💼 Реклама"
    elif any(keyword in text.lower() for keyword in ["бот", "идея", "вопрос"]):
        tag = "💡 Вопрос / идея"

    user_stats[user_id] = user_stats.get(user_id, {"messages": 0, "ads": 0})
    user_stats[user_id]["messages"] += 1
    ticket_id = tickets.get(user_id, next_ticket_id - 1)
    tickets[user_id] = ticket_id

    notification = (
        f"⚡ Новый запрос от пользователя\n"
        f"👤 @{username} (id: {user_id})\n"
        f"🆔 Ticket #{ticket_id}\n"
        f"📩 Сообщение: {text}\n"
        f"🏷 {tag}"
    )

    if user_id in user_states and user_states[user_id] == 'waiting_proposal':
        bot.forward_message(CREATOR_CHAT_ID, message.chat.id, message.message_id)
        bot.send_message(CREATOR_CHAT_ID, notification)
        bot.send_message(message.chat.id, "Ваше предложение передано. Мы свяжемся с вами!")
        del user_states[user_id]
    elif message.text not in ["💼 Сотрудничество", "💸 Поддержать", "📩 Отправить медиа"]:
        bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_CHAT_ID, notification)
        bot.send_message(message.chat.id, "Спасибо! Ваша идея передана. Отвечу, если админ захочет ответить.")

@bot.message_handler(commands=['stats'])
def send_stats(message):
    if message.chat.id not in admin_users:
        bot.send_message(message.chat.id, "Доступ запрещён.")
        return
    total_users = len(user_stats)
    stats_text = f"📊 Статистика:\n- Пользователей: {total_users}\n"
    for user_id, stats in user_stats.items():
        username = bot.get_chat_member(user_id, user_id).user.username or str(user_id)
        stats_text += f"- @{username} (id: {user_id}): сообщений {stats['messages']}, заявок {stats['ads']}\n"
    bot.send_message(message.chat.id, stats_text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id not in admin_users:
        bot.send_message(message.chat.id, "Доступ запрещён.")
        return
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Укажите текст для рассылки: /broadcast ваш_текст")
        return
    broadcast_text = message.text.split(maxsplit=1)[1]
    for user_id in user_stats.keys():
        bot.send_message(user_id, broadcast_text)
    bot.send_message(message.chat.id, "Рассылка завершена.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.chat.id not in admin_users:
        bot.send_message(message.chat.id, "Доступ запрещён.")
        return
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Укажите ID пользователя: /ban user_id")
        return
    user_id = int(message.text.split()[1])
    if user_id in user_stats:
        del user_stats[user_id]
        del tickets[user_id]
        bot.send_message(message.chat.id, f"Пользователь {user_id} заблокирован.")
    else:
        bot.send_message(message.chat.id, "Пользователь не найден.")

@bot.message_handler(commands=['help'])
def send_help(message):
    if message.chat.id not in admin_users:
        bot.send_message(message.chat.id, "Доступ запрещён.")
        return
    help_text = (
        "🎛 Админ-панель:\n"
        "/stats — показать статистику\n"
        "/broadcast текст — отправить рассылку всем\n"
        "/ban id — заблокировать пользователя\n"
        "/help — показать эту помощь"
    )
    bot.send_message(message.chat.id, help_text)

@server.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK', 200

@server.route('/')
def health_check():
    return 'Service is running', 200

if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    WEBHOOK_URL = f"https://cai-user-qa-1.onrender.com/{TOKEN}"
    bot.set_webhook(url=WEBHOOK_URL)
    server.run(host='0.0.0.0', port=port)

