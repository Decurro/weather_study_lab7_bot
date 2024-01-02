from logger import logger
import os
import requests
import datetime
from aiogram import types
from dotenv import load_dotenv
from dispatcher import dp

load_dotenv()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет, я бот для прогноза погоды. Чтобы получить прогноз, просто введи название города!")


@dp.message_handler()
async def send_welcome(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        response_coords = requests.get(
            f'https://api.openweathermap.org/geo/1.0/direct?q={message.text}&limit=1&appid={os.getenv("API_TOKEN")}'
        )
        response_coords = response_coords.json()

        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/air_pollution?lat={response_coords[0].get("lat")}&lon={response_coords[0].get("lon")}&appid={os.getenv("API_TOKEN")}'
        )
        data_air_pollution = response.json()

        data_gases = data_air_pollution['list'][0]['components']
        co = data_gases['co']
        nh3 = data_gases['nh3']
        no = data_gases['no']
        no2 = data_gases['no2']
        o3 = data_gases['o3']
        so2 = data_gases['so2']

        response_weather = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={message.text}&lang=ru&cnt=3&appid={os.getenv("API_TOKEN")}&units=metric'
        )
        data_weather = response_weather.json()
        city = data_weather['name']

        weather_description = data_weather['weather'][0]['main']
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = 'Посмотри в окно, не пойму что там за погода'
        humidity = data_weather['main']['humidity']
        pressure = data_weather['main']['pressure']
        cur_temp = data_weather['main']['temp']
        wind = data_weather['wind']['speed']
        sunrise_timestamp = datetime.datetime.fromtimestamp(data_weather['sys']['sunrise'])

        await message.reply(
            f'***{datetime.datetime.now().strftime("%H:%M - %m.%d.%Y года")}***\n'
            f'Погода в городе: {city}\nТемпература: {cur_temp}C° {wd}\n'
            f'Атмосферное давление: {pressure} мм.рт.ст\nВлажность: {humidity} %\n'
            f'Скорось ветра: {wind} м/с\nВосход солнца: {sunrise_timestamp}\n'
            f'Содержание газов в атмосфере (μg/m3):\n'
            f'Оксид углерода(CO): {co}\n'
            f'Оксид азота(NO): {no}\n'
            f'Диоксид азота(NO2): {no2}\n'
            f'Озон(O3): {o3}\n'
            f'Диоксид серы(SO2): {so2}\n'
            f'Аммиак(NH3) : {nh3}\n'
            f'***Хорошего дня!***')

    except Exception as e:
        await message.reply('\U00002620 Проверьте название города \U00002620')
        logger.error(f"Error: {e}")
