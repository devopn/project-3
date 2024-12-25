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
        df = pd.DataFrame(weather)
        df['date'] = pd.to_datetime(df['date'])
        print(df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['max_temp'], mode='lines', name='Max Temperature'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['min_temp'], mode='lines', name='Min Temperature'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['humidity'], mode='lines', name='Humidity (%)'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['wind_speed'], mode='lines', name='Wind Speed (m/s)'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['rain_probability'], mode='lines', name='Rain Probability (%)'))
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
        stops_codes = [get_city_info(stop, config) for stop in stops]
        stops_weather = [get_daily_weather(code['key'], config) for code in stops_codes]


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