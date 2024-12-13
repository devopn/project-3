import pandas as pd

def weather_to_dataframe(weather_data):
    return pd.DataFrame({
        "date": [w.date for w in weather_data],
        "max_temp": [w.max_temp for w in weather_data],
        "min_temp": [w.min_temp for w in weather_data],
        "humidity": [w.humidity for w in weather_data],
        "wind_speed": [w.wind_speed for w in weather_data],
        "rain_probability": [w.rain_probability for w in weather_data],
        "is_bad": [w.is_bad() for w in weather_data]
    })