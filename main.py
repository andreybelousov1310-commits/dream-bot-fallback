import os
import time
from fastapi import FastAPI
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Змінна для збереження часу останнього пінгу від ПК
last_pc_ping = 0

@app.post("/ping")
async def ping_from_pc():
    global last_pc_ping
    last_pc_ping = time.time()
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "Fallback bot is running"}

@dp.message()
async def fallback_handler(message: Message):
    global last_pc_ping
    current_time = time.time()
    
    # Якщо з останнього пінгу від ПК минуло менше 60 секунд — ПК працює, хмара мовчить
    if current_time - last_pc_ping < 60:
        return 
    
    # Якщо ПК мовчить понад 60 секунд (вимкнений) — відповідає заглушка
    await message.answer("🛠 На сервері ведуться технічні роботи. Скоро все відновимо!")

async def run_bot():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
