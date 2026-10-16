import asyncio
import os
from aiogram import Bot, Dispatcher, types

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def maintenance_handler(message: types.Message):
    await message.answer(
        "🛠 **Зверніть увагу:** Зараз ведуться технічні роботи "
        "або тимчасово відсутнє живлення головного сервера.\n\n"
        "Запит не вдалося обробити. Будь ласка, спробуйте надіслати повідомлення пізніше!"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
