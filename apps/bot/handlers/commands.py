from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from apps.bot.keyboards.reply import reply_main_menu


router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    await message.answer(_("Botga xush kelibsiz!"), reply_markup=reply_main_menu())
