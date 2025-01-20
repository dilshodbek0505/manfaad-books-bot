from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from apps.bot.utils.callback_data import * # noqa


def inline_languages():
    inline_keyboard = InlineKeyboardBuilder()

    inline_keyboard.button(text=_("O'zbek🇺🇿"), callback_data=cb_select_language_callback_data(lang=SelectLanguage.UZ))
    inline_keyboard.button(text=_("Rus🇷🇺"), callback_data=cb_select_language_callback_data(lang=SelectLanguage.RU))
    inline_keyboard.button(text=_("Ingliz🇺🇸"), callback_data=cb_select_language_callback_data(lang=SelectLanguage.EN))

    inline_keyboard.adjust(1)
    
    return inline_keyboard.as_markup()