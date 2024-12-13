from flask import Flask, render_template, request, redirect, render_template_string
from config.config import load_config, Config
from src.services.weather import get_daily_weather
from src.services.city import get_city_info
from src.models.Weather import Weather
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.services.weather2df import weather_to_dataframe
config:Config


app = Flask(__name__,
            static_folder='src/static',
            template_folder='src/templates')
dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/'
)

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1(id='title', style={'textAlign': 'center'}),
    dcc.Graph(id='weather-graph'),
])

city_data = {'city': None}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_weather/<int:count>', methods=['GET'])
def get_weather(count:int):
    if count < 1:
        return redirect('/check_weather/1')
    return render_template('form.html', count=count)

@app.route('/view/<city>', methods=['GET'])
def view(city):
    city_data['city'] = city
    return redirect('/dash/')

@dash_app.callback(
    [Output('title', 'children'), Output('weather-graph', 'figure')],
    [Input('weather-graph', 'id'),Input('url', 'pathname')]
)
def update_graph(id, pathname):
    city_code = str(pathname).split('/')[-1]
    
    try:
        weather = get_daily_weather(city_code, config)
        # Example API response simulation
        # weather = [
        #     {'date': '2024-12-13T07:00:00+03:00', 'max_temp': -6.7, 'min_temp': -10.5, 'humidity': 82, 'wind_speed': 25.9, 'rain_probability': 0},
        #     {'date': '2024-12-14T07:00:00+03:00', 'max_temp': -3.9, 'min_temp': -6.9, 'humidity': 88, 'wind_speed': 18.5, 'rain_probability': 0},
        #     {'date': '2024-12-15T07:00:00+03:00', 'max_temp': -3.4, 'min_temp': -4.7, 'humidity': 90, 'wind_speed': 14.8, 'rain_probability': 0},
        #     {'date': '2024-12-16T07:00:00+03:00', 'max_temp': -1.7, 'min_temp': -3.6, 'humidity': 86, 'wind_speed': 13.0, 'rain_probability': 0},
        #     {'date': '2024-12-17T07:00:00+03:00', 'max_temp': -1.5, 'min_temp': -4.4, 'humidity': 77, 'wind_speed': 22.2, 'rain_probability': 0}
        # ]

        df = pd.DataFrame(weather)
        df['date'] = pd.to_datetime(df['date'])
        print(df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['max_temp'], mode='lines', name='Max Temperature'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['min_temp'], mode='lines', name='Min Temperature'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['humidity'], mode='lines', name='Humidity (%)'))
        fig.update_layout(title=f"Weather Forecast",
                          xaxis_title="Date",
                          yaxis_title="Value",
                          legend_title="Metrics")

        return f"Weather Forecast", fig

    except Exception as e:
        return f"An error occurred: {str(e)}", go.Figure()



@app.route('/check_weather', methods=['POST'])
def check_weather():
    try:
        start = request.form['start']
        end = request.form['end']
        count = int(request.form['count'])
        stops = [request.form[f'stop_{i}'] for i in range(count-1)]
    except KeyError:
        return render_template('error.html', error='Неверные данные')
    try:
        city1_code, city2_code = get_city_info(start, config), get_city_info(end, config)
        city1_weather, city2_weather = get_daily_weather(city1_code['key'], config), get_daily_weather(city2_code['key'], config)
        # city1_weather = [{'date': '2024-12-13T07:00:00+03:00', 'max_temp': -6.7, 'min_temp': -10.5, 'humidity': 82, 'wind_speed': 25.9, 'rain_probability': 0}, {'date': '2024-12-14T07:00:00+03:00', 'max_temp': -3.9, 'min_temp': -6.9, 'humidity': 88, 'wind_speed': 18.5, 'rain_probability': 0}, {'date': '2024-12-15T07:00:00+03:00', 'max_temp': -3.4, 'min_temp': -4.7, 'humidity': 90, 'wind_speed': 14.8, 'rain_probability': 0}, {'date': '2024-12-16T07:00:00+03:00', 'max_temp': -1.7, 'min_temp': -3.6, 'humidity': 86, 'wind_speed': 13.0, 'rain_probability': 0}, {'date': '2024-12-17T07:00:00+03:00', 'max_temp': -1.5, 'min_temp': -4.4, 'humidity': 77, 'wind_speed': 22.2, 'rain_probability': 0}]
        # city2_weather = [{'date': '2024-12-13T07:00:00+10:00', 'max_temp': -5.1, 'min_temp': -10.9, 'humidity': 44, 'wind_speed': 20.4, 'rain_probability': 0}, {'date': '2024-12-14T07:00:00+10:00', 'max_temp': -4.9, 'min_temp': -8.5, 'humidity': 41, 'wind_speed': 11.1, 'rain_probability': 0}, {'date': '2024-12-15T07:00:00+10:00', 'max_temp': -5.8, 'min_temp': -11.0, 'humidity': 45, 'wind_speed': 20.4, 'rain_probability': 0}, {'date': '2024-12-16T07:00:00+10:00', 'max_temp': -4.5, 'min_temp': -13.6, 'humidity': 40, 'wind_speed': 14.8, 'rain_probability': 0}, {'date': '2024-12-17T07:00:00+10:00', 'max_temp': -9.3, 'min_temp': -15.4, 'humidity': 47, 'wind_speed': 22.2, 'rain_probability': 0}]
        stops_codes = [get_city_info(stop, config) for stop in stops]
        stops_weather = [get_daily_weather(code['key'], config) for code in stops_codes]
        # stops_weather =  [
        #     [{'date': '2024-12-13T07:00:00+03:00', 'max_temp': -3.6, 'min_temp': -9.4, 'humidity': 77, 'wind_speed': 22.2, 'rain_probability': 0}, {'date': '2024-12-14T07:00:00+03:00', 'max_temp': -3.8, 'min_temp': -5.5, 'humidity': 69, 'wind_speed': 18.5, 'rain_probability': 0}, {'date': '2024-12-15T07:00:00+03:00', 'max_temp': 1.1, 'min_temp': -2.2, 'humidity': 82, 'wind_speed': 20.4, 'rain_probability': 9}, {'date': '2024-12-16T07:00:00+03:00', 'max_temp': 0.5, 'min_temp': -1.6, 'humidity': 82, 'wind_speed': 16.7, 'rain_probability': 1}, {'date': '2024-12-17T07:00:00+03:00', 'max_temp': 1.0, 'min_temp': -0.3, 'humidity': 84, 'wind_speed': 22.2, 'rain_probability': 4}],
        #     [{'date': '2024-12-13T07:00:00+03:00', 'max_temp': 5.7, 'min_temp': -6.6, 'humidity': 79, 'wind_speed': 13.0, 'rain_probability': 92}, {'date': '2024-12-14T07:00:00+03:00', 'max_temp': 2.6, 'min_temp': -2.8, 'humidity': 57, 'wind_speed': 14.8, 'rain_probability': 0}, {'date': '2024-12-15T07:00:00+03:00', 'max_temp': 11.1, 'min_temp': 6.3, 'humidity': 48, 'wind_speed': 16.7, 'rain_probability': 3}, {'date': '2024-12-16T07:00:00+03:00', 'max_temp': 8.0, 'min_temp': 4.8, 'humidity': 81, 'wind_speed': 14.8, 'rain_probability': 75}, {'date': '2024-12-17T07:00:00+03:00', 'max_temp': 8.8, 'min_temp': 5.9, 'humidity': 81, 'wind_speed': 14.8, 'rain_probability': 95}]
        #     ]

    except Exception as e:
        return render_template('error.html', error=str(e))
    
    try:
        city1_weather = [Weather(**item) for item in city1_weather]
        city2_weather = [Weather(**item) for item in city2_weather]
        stops_weather = [[Weather(**item) for item in stop] for stop in stops_weather]
    except Exception as e:
        return render_template('error.html', error='Error with API')
    
    result = any([item.is_bad() for item in city1_weather + city2_weather] + [any(w.is_bad() for w in item) for item in stops_weather])
    return render_template('result.html', start=start, end=end,city1_weather=city1_weather, city2_weather=city2_weather,stops=stops, stops_codes=stops_codes, stops_weather=stops_weather, result=result, count=len(stops), start_city=city1_code, end_city=city2_code) 



@app.errorhandler(404)
def error_handler(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def error_handler(e):
    return render_template('error.html', error='Internal server error'), 500

@app.errorhandler(503)
def error_handler(e):
    return render_template('error.html', error='Service unavailable'), 503

if __name__ == '__main__':
    config: Config = load_config()
    app.run()