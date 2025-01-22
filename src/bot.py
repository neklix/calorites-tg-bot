import asyncio
from aiogram import Bot, Dispatcher
from handlers import setup_handlers
from middlewares import LoggingMiddleware
from config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

dp.message.middleware(LoggingMiddleware())
setup_handlers(dp)

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
