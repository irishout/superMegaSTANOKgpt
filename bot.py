import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
from tokens import API, TOKEN
import requests





logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()


# ⁡⁢⁣⁣КОМАНДА СТАРТ⁡
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот, созданный специально для судентов '
                         'МГТУ СТАНКИН, отправь свой запрос', parse_mode = 'HTML')


# ⁡⁢⁣⁣ОБРАБОТЧИК ЛЮБОГО СООБЩЕНИЯ⁡
@dp.message()
async def filter_messages(message: Message):
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
                "content": "You are a useful assistant for MSTU STANKIN students. "
                       "You will communicate with russian students mostly in russian"
            },
            {
                "role": "user",
                "content": message.text
            }
        ],
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    # pprint(data)

    text = data['choices'][0]['message']['content']
    bot_text = text.split('</think>\n\n')[1]

    await message.answer(bot_text, parse_mode = "Markdown")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

