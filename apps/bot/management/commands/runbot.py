import asyncio

from django.core.management.base import BaseCommand
from django.conf import settings

from redis.asyncio.client import Redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware, ConstI18nMiddleware

from apps.bot.middlewares.i18n_middleware import CustomI18nMiddleware
from apps.bot.handlers import setup_handlers
from apps.bot.middlewares import setup_middlewares
from apps.bot.config.config import BOT_TOKEN, REDIS_URL


class Command(BaseCommand):
    help = "Run bot in polling"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Bot started"))
        
        asyncio.run(self.start_bot())
        
    async def start_bot(self):
        redis = await Redis.from_url(REDIS_URL)

        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher(storage=RedisStorage(redis=redis))

        i18n = I18n(path="locales", default_locale="en", domain="messages")
        i18n_middleware = CustomI18nMiddleware(i18n=i18n)
        
        i18n_middleware.setup(dp)

        setup_handlers(dp)
        setup_middlewares(dp)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)