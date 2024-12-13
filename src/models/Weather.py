import time


class Weather:
    def __init__(self,date, max_temp, min_temp, humidity, wind_speed, rain_probability):
        self.date = time.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        self.date = time.strftime('%m-%d', self.date)
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.rain_probability = rain_probability

    def is_bad(self):
        return (
            self.min_temp < 0 or
            self.max_temp > 35 or
            self.wind_speed > 50 or
            self.rain_probability > 70 or 
            self.humidity > 90 or 
            self.humidity < 30
        )
    