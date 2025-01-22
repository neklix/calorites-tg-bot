from validators import validate_float


class ResourceBase:
    def __init__(self):
        self.target = None
        self.consumed = 0

    async def report(self):
        pass

    async def set_target(self, target):
        target = validate_float(target)
        self.target = target

    async def consume(self, value):
        print(value)
        value = validate_float(value)
        print(value)
        self.consumed += value


class Calories(ResourceBase):
    def __init__(self):
        super().__init__()
        self.spent = 0

    async def report(self):
        report_str = f"Набрали: {self.consumed} ккал\n"
        report_str += f"Сожгли: {self.spent} ккал\n"
        report_str += f"Баланс: {self.consumed - self.spent} ккал"
        if self.target is not None:
            report_str += f"\nЦель: {self.target} ккал"
        return report_str

    async def add_workout(self, calories):
        self.spent += calories

    async def calculate_target(self, age, height, weight):
        await self.set_target(10 * weight + 6.25 * height - 5 * age)


class Water(ResourceBase):
    def __init__(self):
        super().__init__()
        self.temperature = 0
        self.train_needs = 0

    async def report(self):
        report_str = f"Выпили: {self.consumed} мл"
        if self.target is not None:
            report_str += f"\nЦель: {self.target} мл"
            if self.temperature > 25:
                report_str += "\nДополнительно выпейте 750 мл воды из-за жаркой погоды (уже учтено в цели)"
        if self.train_needs > 0:
            report_str += f"\nВы тренировались, дополнительно выпейте {self.train_needs} мл"
        return report_str

    async def calculate_target(self, weight, temperature):
        self.temperature = validate_float(temperature)
        await self.set_target(weight * 30 + (750 if temperature > 25 else 0))

    async def add_workout(self, water_needs):
        self.train_needs += water_needs
