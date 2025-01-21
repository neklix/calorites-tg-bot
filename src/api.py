import aiohttp
import asyncio

class APIError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class OpenWeatherMapAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.timeout = 30 # seconds
    
    async def geocoding(self, city_nm):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_nm}&appid={self.api_key}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "coord" not in data:
                            raise APIError("Город не найден")
                        lat = data["coord"].get("lat")
                        lon = data["coord"].get("lon")
                        if lat is None or lon is None:
                            raise APIError("Город не найден")
                        return lat, lon
                    else:
                        print(f"Ошибка OpenWeatherMap API: {response.status}, {await response.text()}")
                        raise APIError("Город не найден")
            except aiohttp.ClientError as e:
                print(f"Ошибка OpenWeatherMap API: {e}")
                raise APIError("Ошибка при запросе к API")
            except asyncio.TimeoutError:
                print("Таймаут при запросе к OpenWeatherMap API")
                raise APIError("Таймаут при запросе к API")
    
    async def get_weather(self, lat, lon):
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,current,alerts&appid={self.api_key}&units=metric"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "daily" not in data or len(data["daily"]) == 0 or "temp" not in data["daily"][0]:
                            raise APIError(f"Не удалось получить прогноз погоды для координат {lat}, {lon}")
                        max_temp = data["daily"][0]["temp"].get("max")
                        if max_temp is None:
                            raise APIError(f"Не удалось получить прогноз погоды для координат {lat}, {lon}")
                        return max_temp
                    else:
                        print(f"Ошибка OpenWeatherMap API: {response.status}, {await response.text()}")
                        raise APIError(f"Не удалось получить прогноз погоды для координат {lat}, {lon}")
            except aiohttp.ClientError as e:
                print(f"Ошибка OpenWeatherMap API: {e}")
                raise APIError("Ошибка при запросе к API")
            except asyncio.TimeoutError:
                print("Таймаут при запросе к OpenWeatherMap API")
                raise APIError("Таймаут при запросе к API")

class FoodAPI:
    def __init__(self):
        self.timeout = 30
    
    async def get_calories(self, food_name):
        # метод почти как в примере дз
        url = ("https://world.openfoodfacts.org/cgi/search.pl?action=process"
               f"&search_terms={food_name}"
               "&json=true&page=1&page_size=1"
               "&fields=product_name%2Cnutriments"
        )
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "products" not in data or len(data["products"]) == 0:
                            raise APIError(f"Продукт {food_name} не найден")
                        product_name = data["products"][0].get("product_name")
                        calories = data["products"][0].get("nutriments", {}).get("energy-kcal_100g")
                        if product_name is None or calories is None:
                            raise APIError(f"Продукт {food_name} не найден или для него не найдено количество калорий")
                        return product_name, calories
                    else:
                        print(f"Ошибка OpenFoodFacts API: {response.status}, {await response.text()}")
            except aiohttp.ClientError as e:
                print(f"Ошибка OpenFoodFacts API: {e}")
                raise APIError("Ошибка при запросе к API")
            except asyncio.TimeoutError:
                print("Таймаут при запросе к OpenFoodFacts API")
                raise APIError("Таймаут при запросе к API")

class TrainAPI:
    def __init__(self, api_key):
        self.timeout = 30
        self.headers = {"X-Api-Key": api_key}
        
    
    async def get_calories(self, kind, minutes):
        url = f"https://api.api-ninjas.com/v1/caloriesburned?activity={kind}&time={minutes}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=self.timeout, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if len(data) == 0:
                            raise APIError(f"Тренировка {kind} не найдена")
                        calories = data[0].get("total_calories")
                        name = data[0].get("name")
                        if calories is None or name is None:
                            raise APIError(f"Тренировка {kind} не найдена")
                        return name, calories
                    else:
                        print(f"Ошибка api-ninjas API: {response.status}, {await response.text()}")
                        raise APIError(f"Тренировка {kind} не найдена")
            except aiohttp.ClientError as e:
                print(f"Ошибка api-ninjas API: {e}")
                raise APIError("Ошибка при запросе к API")
            except asyncio.TimeoutError:
                print("Таймаут при запросе к api-ninjas API")
                raise APIError("Таймаут при запросе к API")

