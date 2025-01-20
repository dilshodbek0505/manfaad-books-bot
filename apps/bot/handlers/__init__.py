from .commands import router as commands_router
from .settings import router as settings_router


def setup_handlers(dp):
    dp.include_router(commands_router)
    dp.include_router(settings_router)