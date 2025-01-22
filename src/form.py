from aiogram.fsm.state import State, StatesGroup

class UserInfoForm(StatesGroup):
    name = State()
    age = State()
    height = State()
    weight = State()
    city = State()

class TargetsForm(StatesGroup):
    calories = State()
    water = State()
