import asyncio
from datetime import datetime, timezone
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from fastapi import FastAPI
import uvicorn

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Заглушка, яку бачитимуть користувачі, коли ПК вимкнений
@dp.message(F.text)
async def fallback_handler(message: Message):
    await message.answer(
        "⚠️ Головний сервер на обслуговуванні. Зараз працює резервна система, незабаром усе відновиться."
    )

app = FastAPI()

# Змінна для збереження часу останнього пінгу від ПК
last_ping_time = datetime.now(timezone.utc)
# Головна зміна: при стартовому запуску хмара вважає ПК неактивним, 
# поки не отримає живий пінг (це запобігає миттєвому конфлікту за getUpdates)
is_pc_online = False
polling_task = None


@app.post("/ping")
async def receive_ping():
    global last_ping_time, is_pc_online
    last_ping_time = datetime.now(timezone.utc)
    is_pc_online = True
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "Fallback bot is running", "pc_online": is_pc_online}


async def run_bot_polling():
    """Запускає опитування Telegram, коли ПК офлайн."""
    try:
        print("Запуск фонового Telegram-бота (режим заглушки)...")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        print(f"Помилка в polling: {e}")


async def monitor_heartbeat():
    """Стежить за пінгами від ПК і керує станом бота."""
    global is_pc_online, polling_task
    while True:
        await asyncio.sleep(10)
        now = datetime.now(timezone.utc)
        diff = (now - last_ping_time).total_seconds()

        # Якщо пінг відсутній більше 60 секунд — вважаємо ПК вимкненим
        if diff > 60 and is_pc_online:
            is_pc_online = False
            print("ПК офлайн! Запускаємо хмарного бота...")
            if not polling_task or polling_task.done():
                polling_task = asyncio.create_task(run_bot_polling())

        # Якщо ПК знову в мережі, а polling запущений — зупиняємо його
        elif diff <= 60 and not is_pc_online:
            is_pc_online = True
            print("ПК знову в мережі! Зупиняємо хмарного бота...")
            if polling_task and not polling_task.done():
                await dp.stop_polling()
                polling_task.cancel()


@app.on_event("startup")
async def startup_event():
    # Запускаємо фоновий моніторинг пінгу при старті FastAPI
    asyncio.create_task(monitor_heartbeat())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
