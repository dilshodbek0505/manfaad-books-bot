from enum import Enum
from aiogram.filters.callback_data import CallbackData


class SelectLanguage(str, Enum):
    UZ = 'uz'
    RU = 'ru'
    EN = 'en'

class SelectLanguageCallbackData(CallbackData, prefix="select_language"):
    language: SelectLanguage

def cb_select_language_callback_data(lang):
    return SelectLanguageCallbackData(language=lang.value).pack()

class SelectSearch(str, Enum):
    NAME = 'name'
    author = 'author'
    all_books = 'all'

class SelectSearchCallbackData(CallbackData, prefix="select_search"):
    searching: SelectSearch

def cb_SelectSearch_callback_data(search):
    return SelectSearchCallbackData(searching=search.value).pack()