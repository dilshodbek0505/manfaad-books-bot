from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from apps.bot.keyboards.reply import reply_main_menu, reply_contact
from apps.bot.keyboards.inline import inline_languages
from apps.bot.utils.states import RegisterStatesGroup
from apps.bot.utils.callback_data import SelectLanguageCallbackData

from django.contrib.auth import get_user_model
from django.core.cache import cache


router = Router()
User = get_user_model()


@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    try:
        user = await User.objects.aget(id = message.from_user.id)    

        await message.answer(_("Botga xush kelibsiz!"), reply_markup=reply_main_menu())

    except Exception as err:
        await message.answer(_("Keling siz bilan yaqindan tanishib olamiz 😊"))
        await message.answer(_("Ismingiz: "))
        await state.set_state(RegisterStatesGroup.full_name)


@router.message(F.text, RegisterStatesGroup.full_name)
async def register_full_name(messages: types.Message, state: FSMContext):
    await state.update_data({
        "full_name": messages.text
    })

    await messages.answer(_("Telfon raqamingizni yuboring:"), reply_markup=reply_contact())
    await state.set_state(RegisterStatesGroup.phone)

@router.message(F.text, RegisterStatesGroup.phone)
async def register_phone_text(messages: types.Message, state: FSMContext):
    await state.update_data({
        "phone": messages.text
    })
    
    await messages.answer(_("Tilni tanlang: "), reply_markup=inline_languages())
    await state.set_state(RegisterStatesGroup.language)

@router.message(F.contact, RegisterStatesGroup.phone)
async def register_phone_contact(messages: types.Message, state: FSMContext):
    await state.update_data({
        "contact": messages.contact.phone_number
    })

    await messages.answer(_("Tilni tanlang: "), reply_markup=inline_languages())
    await state.set_state(RegisterStatesGroup.language)

@router.callback_query(RegisterStatesGroup.language, SelectLanguageCallbackData.filter())
async def register_langauge(callback_query: types.CallbackQuery, callback_data: SelectLanguageCallbackData, state: FSMContext):
    from apps.bot.management.commands.runbot import i18n

    cache_key = f"user_language_{callback_query.from_user.id}"
    await cache.aset(cache_key, callback_data.language.value)
    
    i18n.ctx_locale.set(callback_data.language.value)

    data = await state.get_data()
    
    try:
        await User.objects.acreate(
            id = callback_query.from_user.id,
            phone = data.get('phone'),
            first_name = data.get('full_name'),
            language = callback_data.language.value
        )
    except Exception as err:
        await callback_query.message.answer(_("Xatolik yuz berdi 😢"))
        
    await callback_query.message.answer(_("Botga xush kelibsiz!"), reply_markup=reply_main_menu())

    await state.clear()

    await callback_query.answer(cache_time=0)