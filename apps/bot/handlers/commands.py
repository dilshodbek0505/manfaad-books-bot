from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from apps.bot.keyboards.reply import reply_main_menu
from apps.bot.utils.states import RegisterStatesGroup

from django.contrib.auth import get_user_model

router = Router()
User = get_user_model()


@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    try:
        user = await User.objects.aget(id = message.from_user.id)    

        if user:
            await message.answer(_("Botga xush kelibsiz!"), reply_markup=reply_main_menu())

        else:
            await message.answer(_("Keling siz bilan yaqindan tanishib olamiz 😊"))
            await message.answer(_("Ismingiz: "))
            await state.set_state(RegisterStatesGroup.full_name)
        
    except Exception as err:
        await message.answer(_("Xatolik yuz berdi 😢"))


@router.message(F.text, RegisterStatesGroup.full_name)
def register_full_name(messages: types.Message, state: FSMContext):
    ...