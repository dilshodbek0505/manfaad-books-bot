import environ, os

from django.conf import settings


env = environ.Env()
env.read_env(os.path.join(settings.BASE_DIR, ".env"))

BOT_TOKEN = env.str("BOT_TOKEN")
REDIS_URL = env.str("REDIS_URL")

SUBSCRIPTION_CHANNEL_ID = 0