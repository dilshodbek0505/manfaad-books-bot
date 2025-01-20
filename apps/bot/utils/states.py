from aiogram.fsm.state import State, StatesGroup


class SettingsMenuStatesGruop(StatesGroup):
    menu = State()
    language = State()

class RegisterStatesGroup(StatesGroup):
    full_name = State()
    phone = State()
    language = State()