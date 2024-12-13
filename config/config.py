
from dataclasses import dataclass
from config.base import getenv
from dotenv import load_dotenv

load_dotenv() 

@dataclass
class AccuWeather:
    daily_api:str


@dataclass
class Config:
    accuweather: AccuWeather

def load_config() -> Config:
    return Config(
        accuweather=AccuWeather(
            daily_api=getenv('DAILY_API')
        )
    )