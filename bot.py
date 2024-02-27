import asyncio
from aiogram import Bot, Dispatcher
from handlers import generate_post
from dotenv import load_dotenv
import os

# Запуск бота
async def main():
    load_dotenv()
    bot = Bot(token=os.environ.get("BOT_TOKEN"))
    dp = Dispatcher()

    dp.include_routers(generate_post.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())