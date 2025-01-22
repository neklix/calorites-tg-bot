import asyncio
from validators import validate_str, validate_int, validate_float
from resources import Water, Calories


class UserInfo:
    def __init__(self):
        self.name = None
        self.age = None
        self.geo = None
        self.height = None
        self.weight = None

    async def set_name(self, name):
        self.name = validate_str(name)

    async def set_geo(self, city, lat, lon):
        self.geo = {}
        self.geo["city"] = validate_str(city)
        self.geo["lat"] = validate_float(lat)
        self.geo["lon"] = validate_float(lon)

    async def set_age(self, age):
        self.age = validate_int(age)

    async def set_height(self, height):
        self.height = validate_float(height)

    async def set_weight(self, weight):
        self.weight = validate_float(weight)

    async def get_all_info(self):
        return (""
        f"Ваше имя: {self.name}\n"
        f"Ваш возраст: {self.age}\n"
        f"Ваш город: {self.geo['city']} ({self.geo['lat']}, {self.geo['lon']})\n"
        f"Ваш рост (см): {self.height}\n"
        f"Ваш вес (кг): {self.weight}")

    async def is_form_filled(self):
        return all([self.name, self.age, self.geo, self.height, self.weight])

    async def get_geo(self):
        return self.geo


class User(UserInfo):
    def __init__(self, uid):
        super().__init__()
        self.id = uid
        self.water = Water()
        self.calories = Calories()

    async def reset_progress(self, save_targets, temperature=0):
        if save_targets:
            calories_target = self.calories.target
            water_target = self.water.target
            self.calories = Calories()
            self.water = Water()
            await asyncio.gather(
                self.calories.set_target(calories_target),
                self.water.set_target(water_target)
            )
        else:
            self.water = Water()
            self.calories = Calories()
            await asyncio.gather(
                self.calories.calculate_target(self.age, self.height, self.weight),
                self.water.calculate_target(self.weight, temperature)
            )

    async def get_report(self):
        is_form_filled = await self.is_form_filled()
        if not is_form_filled:
            return "Заполните, пожалуйста, всю информацию о себе с помощью команды /fill_info"
        (calories_report, water_report) = await asyncio.gather(
            self.calories.report(), self.water.report())
        return (f"Ваши результаты по калориям:\n{calories_report}\n\n"
                f"Ваши результаты по воде:\n{water_report}")

    async def add_workout(self, calories, water):
        return await asyncio.gather(
            self.calories.add_workout(calories),
            self.water.add_workout(water)
        )
