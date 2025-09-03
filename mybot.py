import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (замените на свой или используйте переменную окружения)
BOT_TOKEN = os.getenv('BOT_TOKEN', '7607974434:AAHUdxPeuP4agNFMnwT-s-WmzCs3boMlAQY')

# ID администратора и создателя (замените на реальные user_id, usernames не работают для отправки)
# Чтобы получить user_id, бот должен взаимодействовать с пользователем или использовать другие методы
ADMIN_ID = 217784938  # Замените на реальный user_id @sten_anyqx
CREATOR_ID = 897127957  # Замените на реальный user_id @vl_std

# Определение состояний FSM
class AdvertisingState(StatesGroup):
    waiting = State()  # Состояние ожидания сообщений для заказа рекламы

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хэндлер для команды /start
@dp.message(Command('start'))
async def start_handler(message: types.Message, state: FSMContext):
    # Сброс состояния на всякий случай
    await state.clear()
    
    # Создание inline-клавиатуры
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поддержать 💸", callback_data="support")],
        [InlineKeyboardButton(text="Сотрудничество 🤝", callback_data="cooperation")]
    ])
    
    await message.answer("Добро пожаловать! 😊 Выберите опцию:", reply_markup=keyboard)

# Хэндлер для inline-кнопок
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "support":
        await callback.message.answer("Вы можете поддержать нас, отправив USDT на адрес: TVkXgDHJsMQcR14Mr6uPdpELqJuG6Aok5L через сеть TRC20. 🙌")
    
    elif callback.data == "cooperation":
        text = (
            "Авторазделение по темам: сотрудничество 🤝\n"
            "Список прайса:\n"
            "1. Ваш пост в одном из тг каналов @characterhh или @janitorai6 - 10$ 📢\n"
            "2. Мой обзор и публикация поста о Вашем продукте/канале/приложении в одном из моих каналов - 30$ 📝\n"
            "3. Короткий ролик до 10 секунд о Вашем продукте на тик ток аккаунт - 50$ 🎥\n"
            "4. Разговорный рекламный ролик отзыв о Вашем продукте - 99$ 🎙️\n"
            "\n"
            "Все подробности и нюансы обсуждаются лично. 😊"
        )
        # Кнопка "Хочу заказать рекламу"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Хочу заказать рекламу 🚀", callback_data="order_ad")]
        ])
        await callback.message.answer(text, reply_markup=keyboard)
    
    elif callback.data == "order_ad":
        await callback.message.answer("Здравствуйте! 😊 Мы рады сотрудничать с Вами. Слушаем внимательно Ваше предложение! 🎉")
        # Вход в состояние заказа рекламы
        await state.set_state(AdvertisingState.waiting)
    
    await callback.answer()  # Закрыть callback

# Хэндлер для команды /stop (выход из режима)
@dp.message(Command('stop'))
async def stop_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AdvertisingState.waiting:
        await state.clear()
        await message.answer("Вы вышли из режима заказа рекламы. 😌")
    else:
        await message.answer("Вы не в режиме заказа рекламы. 🤔")

# Хэндлер для всех сообщений (текст, фото, видео)
@dp.message()
async def message_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    sender_username = message.from_user.username or f"ID_{message.from_user.id}"
    target_id = CREATOR_ID if current_state == AdvertisingState.waiting else ADMIN_ID
    
    try:
        # Пересылка сообщения
        await bot.forward_message(
            chat_id=target_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        # Логирование успешной пересылки
        logger.info(f"Message from @{sender_username} forwarded to {target_id}")
    except Exception as e:
        # Обработка ошибок (например, нет прав или чат недоступен)
        logger.error(f"Error forwarding message from @{sender_username} to {target_id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего сообщения. 😔 Пожалуйста, попробуйте позже.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
