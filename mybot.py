import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("No BOT_TOKEN environment variable set")

# Replace with actual chat IDs
ADMIN_CHAT_ID = 123456789  # Chat ID for @sten_anyqx (get it by sending a message to the bot and checking update)
CREATOR_CHAT_ID = 987654321  # Chat ID for @vl_std (same as above)

WALLET_ADDRESS = 'TVkXgDHJsMQcR14Mr6uPdpELqJuG6Aok5L'
NETWORK = 'TRC20'

bot = telebot.TeleBot(TOKEN)

# Dictionary to track user states
user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет!\n\n"
        "Хочешь задать вопрос? У тебя есть идея для поста/видео? Хочешь обгарнится с рекламой?\n"
        "Или ты хочешь поделиться с сообществом крутым про ИИ ботов?\n"
        "Пиши мне смело 😊\n\n"
        "Я читаю всё с теплом и вниманием 💜"
    )
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Сотрудничество"))
    markup.add(KeyboardButton("Поддержать"))
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Поддержать")
def handle_support(message):
    support_text = (
        f"Поддержите нас через USDT via сеть {NETWORK}:\n"
        f"{WALLET_ADDRESS}\n\n"
        "Спасибо за вашу поддержку! 😊"
    )
    bot.send_message(message.chat.id, support_text)

@bot.message_handler(func=lambda message: message.text == "Сотрудничество")
def handle_cooperation(message):
    price_list = (
        "Авторазделение по темам: сотрудничество.\n\n"
        "Список прайса:\n"
        "1. Ваш пост в одном из тг каналов @characterhh или @janitorai6 - 10$\n"
        "2. Мой обзор и публикация поста о Вашем продукте/канале/приложении в одном из моих каналов - 30$\n"
        "3. Короткий ролик до 10 секунд о Вашем продукте на тик ток аккаунт - 50$\n"
        "4. Разговорный рекламный ролик отзыв о Вашем продукте - 99$\n\n"
        "Все подробности и нюансы обсуждаются лично."
    )
    
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(InlineKeyboardButton("Хочу заказать рекламу", callback_data="order_ad"))
    
    bot.send_message(message.chat.id, price_list, reply_markup=inline_markup)

@bot.callback_query_handler(func=lambda call: call.data == "order_ad")
def handle_order_ad(call):
    bot.answer_callback_query(call.id)
    greeting = "Здравствуйте! Мы рады сотрудничать с Вами. Слушаем внимательно Ваше предложение."
    bot.send_message(call.message.chat.id, greeting)
    
    # Set state to wait for proposal
    user_states[call.from_user.id] = 'waiting_proposal'

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == 'waiting_proposal':
        # Forward to creator
        bot.forward_message(CREATOR_CHAT_ID, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "Ваше предложение передано. Мы свяжемся с вами!")
        del user_states[user_id]
    elif message.text not in ["Сотрудничество", "Поддержать"]:
        # Forward to admin
        bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "Спасибо! Ваша идея передана. Отвечу, если админ захочет ответить.")

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
        raise
