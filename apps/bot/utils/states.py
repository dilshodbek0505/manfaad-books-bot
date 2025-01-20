from aiogram.fsm.state import State, StatesGroup


class SettingsMenuStatesGruop(StatesGroup):
    menu = State()
    language = State()

