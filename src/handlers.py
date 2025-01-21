from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from form import UserInfoForm, TargetsForm
from validators import validate_float, validate_int, ValidationError
from storage import Storage
from api import OpenWeatherMapAPI, FoodAPI, TrainAPI, APIError
from config import WEATHER_TOKEN, TRAIN_TOKEN

router = Router()
users_storage = Storage()
owm_api = OpenWeatherMapAPI(WEATHER_TOKEN)
food_api = FoodAPI()
train_api = TrainAPI(TRAIN_TOKEN)

async def apply_or_check_existing(user_id, func):
    try:
        return True, await users_storage.apply(user_id, func)
    except ValidationError as e:
        raise e
    except ValueError:
        return False, "Ваших данных нет в базе.\n" \
               "Для ввода данных введите команду /fill_info"

@router.message(Command("help"))
async def cmd_help(message: Message):
    is_user_in_storage = await users_storage.exists(message.from_user.id)
    if not is_user_in_storage:
        await message.reply("Доступные команды:\n"
                            "/start - начало работы с ботом\n"
                            "/fill_info - заполнить информацию о себе\n"
                            "/help - список доступных команд\n"
        )
        return
    is_user_form_filled, _ = await apply_or_check_existing(message.from_user.id, lambda x: x.is_form_filled())
    if not is_user_form_filled:
        await message.reply("Доступные команды:\n"
                            "/start - начало работы с ботом\n"
                            "/fill_info - заполнить информацию о себе\n"
                            "/reset_info - сбросить информацию о себе\n"
                            "/get_info - получить информацию о себе\n"
                            "/help - список доступных команд\n"
        )
        return
    await message.reply("Доступные команды:\n"
                        "/start - начало работы с ботом\n"
                        "/get_info - получить информацию о себе\n"
                        "/reset_info - сбросить информацию о себе\n"
                        "/check_progress - получить информацию о прогрессе по достижению целей\n"
                        "/reset_progress - сбросить прогресс и цели\n"
                        "/log_water <количество в мл> - записать количество выпитой воды\n"
                        "/log_workout <название активности> <длительность в минутах> - записать тренировку\n"
                        "/log_food <название> <количество (в граммах)> - записать прием пищи\n"
                        "/set_water_target - установить цель по воде\n"
                        "/set_calories_target - установить цель по калориям\n"
                        "/help - список доступных команд\n"
    )



@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Для начала работы с ботом введите команду /fill_info и заполните информацию о себе.\n"
                        "Для просмотра доступных команд введите /help"
                        )

@router.message(Command("get_info"))
async def get_info(message: Message):
    user_id = message.from_user.id
    is_user_in_storage, user_info = await apply_or_check_existing(user_id, lambda x: x.get_all_info())
    if is_user_in_storage:
        await message.reply("Ваши данные в базе:\n"
                            f"{user_info}\n"
                            "Для очистки данных введите команду /reset_info")
    else:
        await message.reply(user_info)

@router.message(Command("fill_info"))
async def fill_info(message: Message, state: FSMContext):
    user_id = message.from_user.id
    create_done = await users_storage.create_user(user_id)
    if not create_done:
        user_info = await users_storage.apply(user_id, lambda x: x.get_all_info())
        await message.reply("Ваши данные уже есть в базе.\n"
                            f"{user_info}\n"
                            "Для очистки данных введите команду /reset_info\n"
                            "Для просмотра доступных команд введите /help")
        return
    await message.reply("Введите Ваше имя")
    await state.set_state(UserInfoForm.name)

@router.message(Command("reset_info"))
async def reset_info(message: Message):
    user_id = message.from_user.id
    await users_storage.delete_user(user_id)
    await message.reply("Данные профиля удалены из базы.\nДля заполнения профиля введите команду /fill_info")

@router.message(UserInfoForm.name)
async def fill_name(message: Message, state: FSMContext):
    try:
        await users_storage.apply(message.from_user.id, lambda x: x.set_name(message.text))
    except ValueError:
        await message.reply("Произошла ошибка, попробуйте ввести имя еще раз.")
        return
    await message.reply("Введите Ваш возраст (целое число)")
    await state.set_state(UserInfoForm.age)
    
@router.message(UserInfoForm.age)
async def fill_age(message: Message, state: FSMContext):
    try:
        await users_storage.apply(message.from_user.id, lambda x: x.set_age(message.text))
    except ValueError:
        await message.reply("Произошла ошибка, попробуйте ввести возраст (целое число) еще раз.")
        return
    await message.reply("Введите Ваш город")
    await state.set_state(UserInfoForm.city)

@router.message(UserInfoForm.city)
async def fill_city(message: Message, state: FSMContext):
    try:
        city_name = message.text
        lat, lon = await owm_api.geocoding(city_name)
        await users_storage.apply(message.from_user.id, lambda x: x.set_geo(city=city_name, lat=lat, lon=lon))
    except APIError as e:
        await message.reply(f"{e.message}\nПопробуйте ввести город еще раз")
        return
    except ValueError:
        await message.reply("Произошла ошибка, попробуйте ввести город еще раз.")
        return
    await message.reply("Введите Ваш рост (в сантиметрах)")
    await state.set_state(UserInfoForm.height)

@router.message(UserInfoForm.height)
async def fill_height(message: Message, state: FSMContext):
    try:
        await users_storage.apply(message.from_user.id, lambda x: x.set_height(message.text))
    except ValueError:
        await message.reply("Произошла ошибка, попробуйте ввести рост (целое число, в сантиметрах) еще раз.")
        return
    await message.reply("Введите Ваш вес (в кг)")
    await state.set_state(UserInfoForm.weight)

@router.message(UserInfoForm.weight)
async def fill_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        await users_storage.apply(user_id, lambda x: x.set_weight(message.text))
    except ValueError:
        await message.reply("Произошла ошибка, попробуйте ввести вес (целое число, в кг) еще раз.")
        return
    _, result = await apply_or_check_existing(user_id, lambda x: x.get_geo())
    try:
        temperature = await owm_api.get_weather(result["lat"], result["lon"])
    except APIError:
        temperature = 0
    await users_storage.apply(user_id, lambda x: x.reset_progress(save_targets=False, temperature=temperature))
    user_info = await users_storage.apply(user_id, lambda x: x.get_all_info())
    await message.reply("Профиль заполнен:\n"
                        f"{user_info}\n"
                        "Для очистки данных введите команду /reset_info\n"
                        "Для просмотра доступных команд введите /help")
    await state.clear()

@router.message(Command("check_progress"))
async def check_progress(message: Message):
    user_id = message.from_user.id
    _, reply = await apply_or_check_existing(user_id, lambda x: x.get_report())
    await message.reply(reply)


@router.message(Command("reset_progress"))
async def reset_progress(message: Message):
    user_id = message.from_user.id
    is_user_in_storage, result = await apply_or_check_existing(user_id, lambda x: x.get_geo())
    if not is_user_in_storage:
        await message.reply(result)
        return
    try:
        temperature = await owm_api.get_weather(result["lat"], result["lon"])
    except APIError:
        temperature = 0
    await apply_or_check_existing(user_id, lambda x: x.reset_progress(save_targets=False, temperature=temperature))
    await message.reply("Прогресс сброшен.")

@router.message(Command("log_water"))
async def log_water(message: Message):
    user_id = message.from_user.id
    water_ml = message.text.split()[-1]
    try:
        is_user_in_storage, reply = await apply_or_check_existing(user_id, lambda x: x.water.consume(water_ml))
    except ValidationError:
        await message.reply(
            "Ошибка в формате.\nВведите количество выпитой воды в миллилитрах после команды, например '/log_water 50'")
        return
    if not is_user_in_storage:
        await message.reply(reply)
        return
    await message.reply(f"Записали употребление {water_ml} мл воды.")

@router.message(Command("log_workout"))
async def log_workout(message: Message):
    user_id = message.from_user.id
    try:
        workout_kind = ' '.join(message.text.split()[1:-1])
        workout_minutes = validate_int(message.text.split()[-1])
        matched_name, workout_calories = await train_api.get_calories(workout_kind, workout_minutes)
        water_needs = 200 * workout_minutes / 30
        is_user_in_storage, reply = await apply_or_check_existing(user_id, lambda x: x.add_workout(workout_calories, water_needs))
    except ValidationError:
        await message.reply(
            "Ошибка в формате.\n"
            "Введите тип и количество минут тренировки после команды, например '/log_workout бег 30'")
        return
    except APIError as e:
        await message.reply(f"{e.message}\nПопробуйте ввести название тренировки еще раз")
        return
    if not is_user_in_storage:
        await message.reply(reply)
        return
    await message.reply(
        f"Записали тренировку {matched_name}, Вы потратили {workout_calories} ккал.\n"
        f"Дополнительно выпейте {water_needs} мл воды.")

async def get_food_calories(food_name, food_amount):
    matched_name, calories_100g = await food_api.get_calories(food_name)
    food_amount = validate_float(food_amount)
    return matched_name, calories_100g, calories_100g * food_amount / 100

@router.message(Command("log_food"))
async def log_food(message: Message):
    user_id = message.from_user.id
    food_name = ' '.join(message.text.split()[1:-1])
    food_amount = message.text.split()[-1]
    try:
        matched_name, calories_100g, calories = await get_food_calories(food_name, food_amount)
        is_user_in_storage, reply = await apply_or_check_existing(user_id, lambda x: x.calories.consume(calories))
    except ValidationError:
        await message.reply(
            "Ошибка в формате.\n"
            "Введите название продукта и его количество (в граммах) после команды, "
            "например '/log_food банан 100'")
        return
    except APIError as e:
        await message.reply(f"{e.message}\nПопробуйте ввести название продукта еще раз")
        return
    if not is_user_in_storage:
        await message.reply(reply)
        return
    await message.reply(f"Найден продукт {matched_name} (в 100г {calories_100g} ккал\nЗаписали {calories}ккал.")

@router.message(Command("set_water_target"))
async def set_water_target(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_exists = await users_storage.exists(user_id)
    if not user_exists:
        await message.reply("Ваших данных нет в базе.\n"
                            "Для ввода данных введите команду /fill_info")
        return
    await message.reply("Введите цель по воде (в миллилитрах).\nЕсли хотите автоматически вычислить цель, введите 'auto'")
    await state.set_state(TargetsForm.water)

@router.message(TargetsForm.water)
async def set_water_target_value(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        if message.text.lower() == 'auto':
            await apply_or_check_existing(user_id, lambda x: x.water.calculate_target())
        else:
            await apply_or_check_existing(user_id, lambda x: x.water.set_target(message.text))
    except ValidationError:
        await message.reply("Ошибка.\nВведите целое число (в миллилитрах), например '1000' или 'auto'")
        return
    await message.reply(
        "Цель по воде установлена.\n"
        "Для изенения цели калорий введите команду /set_calories_target\n"
        "Для изменения цели воды снова введите команду /set_water_target")
    await state.clear()

@router.message(Command("set_calories_target"))
async def set_calories_target(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_exists = await users_storage.exists(user_id)
    if not user_exists:
        await message.reply("Ваших данных нет в базе.\n"
                            "Для ввода данных введите команду /fill_info")
        return
    await message.reply("Введите цель по калориям (в ккал).\nЕсли хотите автоматически вычислить цель, введите 'auto'")
    await state.set_state(TargetsForm.calories)

@router.message(TargetsForm.calories)
async def set_calories_target_value(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        if message.text.lower() == 'auto':
            await apply_or_check_existing(user_id, lambda x: x.calories.calculate_target())
        else:
            await apply_or_check_existing(user_id, lambda x: x.calories.set_target(message.text))
    except ValidationError:
        await message.reply("Ошибка.\nВведите целое число (в ккал), например '1000' или 'auto'")
        return
    await message.reply(
        "Цель по калориям установлена.\n"
        "Для изменения цели воды введите команду /set_water_target\n"
        "Для изенения цели калорий снова введите команду /set_calories_target")
    await state.clear()


def setup_handlers(dp):
    dp.include_router(router)
