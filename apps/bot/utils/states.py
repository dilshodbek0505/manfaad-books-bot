from aiogram.fsm.state import State, StatesGroup


class UpdateLanguageStatesGroup(StatesGroup):
    language = State()