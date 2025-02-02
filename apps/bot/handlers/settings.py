from aiogram import types, Router, F,Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from apps.bot.keyboards.reply import reply_settings_menu, reply_main_menu
from apps.bot.keyboards.inline import inline_languages,inline_searches
from apps.bot.utils.states import SettingsMenuStatesGruop, SearchStatesGruop
from apps.bot.utils.callback_data import SelectLanguageCallbackData,SelectSearchCallbackData

from django.core.cache import cache
from apps.bot.config.config import BOT_TOKEN
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from aiogram.exceptions import TelegramBadRequest

router = Router()
bot = Bot(token=BOT_TOKEN)
User = get_user_model()

@router.message(F.text == __("Sozlamalar⚙️"))
async def settings_menu(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        if "search_message_id" in data:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=data["search_message_id"]
            )
        if "search_message_name" in data:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=data["search_message_name"]
            )
    except TelegramBadRequest:
        pass
    await message.answer(_("Sozlamalar menusi"), reply_markup=reply_settings_menu())
    await state.set_state(SettingsMenuStatesGruop.menu)

@router.message(F.text == __("Kitoblar📚"))
async def Books_search(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        if "search_message_id" in data:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=data["search_message_id"]
            )
        if "search_message_name" in data:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=data["search_message_name"]
            )
    except TelegramBadRequest:
        pass
    
    await state.clear()
    await state.update_data(book_message_id=message.message_id)
    await message.answer(_("Kitoblarni nomi yoki muallifini yozib qidirishingiz mumkin"), reply_markup=inline_searches())
    
    await state.set_state(SearchStatesGruop.books)
    
    

@router.message(F.text == __("Tilni o'zgartirish"), SettingsMenuStatesGruop.menu)
async def settings_change_language(message: types.Message, state: FSMContext):
    await message.answer(_("Tilni tanlang:"), reply_markup=inline_languages())
    await state.clear()
    await state.set_state(SettingsMenuStatesGruop.language)

@router.callback_query(SettingsMenuStatesGruop.language, SelectLanguageCallbackData.filter())
async def settings_select_language(callback_query: types.CallbackQuery, callback_data: SelectLanguageCallbackData, state: FSMContext):
    from apps.bot.management.commands.runbot import i18n
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

    cache_key = f"user_language_{callback_query.from_user.id}" 

    await cache.aset(cache_key, callback_data.language.value)
    
    user = await sync_to_async(lambda: User.objects.filter(pk=callback_query.from_user.id).first())()
    
    i18n.ctx_locale.set(callback_data.language.value)
    if user:
        user.language = callback_data.language.value
        await sync_to_async(user.save)()


    await callback_query.message.answer(_("Sozlamalar menusi"), reply_markup=reply_main_menu())
    await state.set_state(SettingsMenuStatesGruop.menu)

    await callback_query.answer(cache_time=0)