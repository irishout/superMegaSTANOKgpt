from tokens import API, TOKEN
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from aiohttp.client import ClientSession

logger = logging.getLogger(__name__)

TOKEN = TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ⁡⁢⁣⁣КОМАНДА СТАРТ⁡
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот, созданный специально для судентов '
                         'МГТУ СТАНКИН, отправь свой запрос', parse_mode='HTML')


# ⁡⁢⁣⁣ОБРАБОТЧИК ЛЮБОГО СООБЩЕНИЯ⁡
@dp.message()
async def filter_messages(message: Message, state: FSMContext):
    request_expire_at = await state.get_value("request_expire_at")
    if request_expire_at:
        if datetime.now() < request_expire_at:
            return await message.answer("☝️ Обожди, у тебя уже есть активный запрос!")
        await state.clear()

    await state.update_data(request_expire_at=datetime.now() + timedelta(minutes=1))

    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": API,
    }

    data = {
        "model": "deepseek-ai/DeepSeek-R1",
        "messages": [
            {
                "role": "system",
                "content": """You are a useful assistant for MSTU STANKIN students. 
                       You will communicate with russian students mostly in russian
                       Always respond in plain text only. Do not use any LaTeX formatting, 
                       symbols like \\boxed{}, \\[ \\], or any mathematical notation. 
                       Write all numbers, equations, and calculations in simple text format. 
                       For example, say 'The sum of 4 and 4 is 8.' instead of using formatted equations."""
            },
            {
                "role": "user",
                "content": message.text
            }
        ],
    }
    async with ClientSession(headers=headers) as session:
        async with session.post(url, json=data) as response:
            response_data = await response.json()

    text = response_data['choices'][0]['message']['content']
    bot_text = text.split('</think>\n\n')[1]

    await message.answer(bot_text, parse_mode="Markdown")
    await state.clear()


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
