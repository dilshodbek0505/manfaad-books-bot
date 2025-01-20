from aiogram import Router, types, F
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext

from apps.bot.keyboards.reply import reply_settings_menu, reply_main_menu
from apps.bot.keyboards.inline import inline_languages
from apps.bot.utils.states import UpdateLanguageStatesGroup

from django.contrib.auth import get_user_model

router = Router()
User = get_user_model()



@router.message(F.text == __("Sozlamalar"))
async def settings_menu(messages: types.Message, state: FSMContext):
    await messages.answer(_("Sozlamalar menusi"), reply_markup=reply_settings_menu())
    await state.set_state(UpdateLanguageStatesGroup.language)


@router.message(F.text == __("Tilni o'zgartirish"), UpdateLanguageStatesGroup.language)
async def settings_menu_update_language(message: types.Message, state: FSMContext):
    await message.answer(_("Tilni tanlang"), reply_markup=inline_languages())
    

@router.callback_query(UpdateLanguageStatesGroup.language)
async def settings_manu_callback_language(callback_query: types.CallbackQuery, state: FSMContext):
    user, _ = await User.objects.aget_or_create(id = callback_query.from_user.id)
    user.language = callback_query.data.split(":")[1]
    await user.asave()
    
    await state.clear()
    await callback_query.answer(cache_time=0)


