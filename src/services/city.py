import requests
from config.config import Config

def get_city_info(city_name: str, config:Config) -> dict:
    base_url = 'http://dataservice.accuweather.com/locations/v1/cities/search'
    query = {
        'apikey': config.accuweather.daily_api,
        'q': city_name
    }
    try:
        response = requests.get(base_url, params=query)
    except Exception as e:
        raise Exception('Проблемы с подключением к API')
    # print(response.json())
    if response.status_code != 200:
        raise Exception('Проблемы с AccuWeather: ' + str(response.status_code))
    if len(response.json()) == 0:
        raise Exception('Город не найден')
    return {
        'key': response.json()[0]['Key'],
        'name': response.json()[0]['LocalizedName'],
        'lon': response.json()[0]['GeoPosition']['Longitude'],
        'lat': response.json()[0]['GeoPosition']['Latitude']
    }