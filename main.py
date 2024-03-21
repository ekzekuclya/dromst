import os
import django
from asgiref.sync import sync_to_async


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
import environ
env = environ.Env()

env_file_path = '.envs/.bot'
environ.Env.read_env(env_file=env_file_path)
import asyncio
import logging

BOT_TOKEN = env("BOT_TOKEN")


async def periodic_check_orders(bot):
    from auth_app.models import Order
    from bot.handlers.order import order_sender
    while True:
        orders = await sync_to_async(Order.objects.filter)(op_sent=False)
        if orders:
            for order in orders:
                await order_sender(bot=bot, order=order)
        await asyncio.sleep(15)


async def main():
    from aiogram.enums.parse_mode import ParseMode
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram import Bot, Dispatcher
    from bot.handlers import start, order

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(start.router, order.router)

    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(periodic_check_orders(bot=bot))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())