from aiogram.fsm.state import State, StatesGroup


class SettingsMenuStatesGruop(StatesGroup):
    menu = State()
    language = State()

class SearchStatesGruop(StatesGroup):
    books = State()
    search_name = State()
    search_author = State()

class RegisterStatesGroup(StatesGroup):
    full_name = State()
    phone = State()
    language = State()