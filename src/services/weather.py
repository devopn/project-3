import requests 

def get_daily_weather(code, config):
    base_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{code}'
    query = {
        'apikey': config.accuweather.daily_api,
        'metric':True,
        'details':True
    }
    try:
        response = requests.get(base_url, params=query)
    except Exception as e:
        raise Exception('Проблемы с подключением к API')
    if response.status_code == 200:
        result = [
            {
                'date': day['Date'],
                'max_temp': day['Temperature']['Maximum']['Value'],
                'min_temp': day['Temperature']['Minimum']['Value'],
                'humidity': day['Day']['RelativeHumidity']['Average'],
                'wind_speed': day['Day']['Wind']['Speed']['Value'],
                'rain_probability': day['Day']['RainProbability']
            } for day in response.json()['DailyForecasts']
        ]
        return result
    else:
        raise Exception('Проблемы с AccuWeather: ' + str(response.status_code))