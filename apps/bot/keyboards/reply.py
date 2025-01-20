from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def reply_main_menu():
    reply_keyboard = ReplyKeyboardBuilder()

    reply_keyboard.button(text=_("Sozlamalar"))

    return reply_keyboard.as_markup(resize_keyboard = True)

def reply_settings_menu():
    reply_keyboard = ReplyKeyboardBuilder()

    reply_keyboard.button(text=_("Tilni o'zgartirish"))

    return reply_keyboard.as_markup(resize_keyboard = True)