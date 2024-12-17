# app.py
from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

OPENWEATHER_API_KEY = 'f830a70019f17912375c017b8569e85f'
BASE_URL = "http://api.openweathermap.org/data/2.5"

def kelvin_to_celsius(kelvin):
    return round(kelvin - 273.15)

def get_weather_icon_name(code):
    # Mapeamento de códigos do OpenWeather para nomes de ícones personalizados
    weather_icons = {
        '01d': 'sun',
        '01n': 'moon',
        '02d': 'cloud-sun',
        '02n': 'cloud-moon',
        '03d': 'cloud',
        '03n': 'cloud',
        '04d': 'clouds',
        '04n': 'clouds',
        '09d': 'cloud-rain',
        '09n': 'cloud-rain',
        '10d': 'cloud-sun-rain',
        '10n': 'cloud-moon-rain',
        '11d': 'cloud-lightning',
        '11n': 'cloud-lightning',
        '13d': 'snowflake',
        '13n': 'snowflake',
        '50d': 'cloud-fog',
        '50n': 'cloud-fog'
    }
    return weather_icons.get(code, 'question')

def get_current_weather(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY,
        'lang': 'pt_br'
    }
    
    response = requests.get(f"{BASE_URL}/weather", params=params)
    
    if response.status_code == 200:
        data = response.json()
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temp': kelvin_to_celsius(data['main']['temp']),
            'feels_like': kelvin_to_celsius(data['main']['feels_like']),
            'humidity': data['main']['humidity'],
            'wind_speed': round(data['wind']['speed'] * 3.6, 1),
            'description': data['weather'][0]['description'].capitalize(),
            'icon': get_weather_icon_name(data['weather'][0]['icon']),
            'temp_min': kelvin_to_celsius(data['main']['temp_min']),
            'temp_max': kelvin_to_celsius(data['main']['temp_max']),
            'pressure': data['main']['pressure'],
            'visibility': data['visibility'] // 1000,  # converter para km
            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
        }
    return None

def get_forecast(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY,
        'lang': 'pt_br'
    }
    
    response = requests.get(f"{BASE_URL}/forecast", params=params)
    
    if response.status_code == 200:
        data = response.json()
        daily_forecasts = []
        
        # Agrupar previsões por dia
        current_date = None
        daily_data = None
        
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt'])
            if current_date != date.date():
                if daily_data:
                    daily_forecasts.append(daily_data)
                current_date = date.date()
                daily_data = {
                    'date': date.strftime('%d/%m'),
                    'day_name': date.strftime('%A').capitalize(),
                    'temp_min': kelvin_to_celsius(item['main']['temp_min']),
                    'temp_max': kelvin_to_celsius(item['main']['temp_max']),
                    'icon': get_weather_icon_name(item['weather'][0]['icon']),
                    'description': item['weather'][0]['description'].capitalize()
                }
            else:
                # Atualizar temperaturas mín/máx se necessário
                daily_data['temp_min'] = min(daily_data['temp_min'], 
                                           kelvin_to_celsius(item['main']['temp_min']))
                daily_data['temp_max'] = max(daily_data['temp_max'], 
                                           kelvin_to_celsius(item['main']['temp_max']))
        
        if daily_data:
            daily_forecasts.append(daily_data)
        
        return daily_forecasts[:5]  # Retorna previsão para 5 dias
    return None

def get_air_quality(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY
    }
    
    response = requests.get(f"{BASE_URL}/air_pollution", params=params)
    
    if response.status_code == 200:
        data = response.json()
        aqi = data['list'][0]['main']['aqi']
        aqi_labels = {
            1: {'label': 'Boa', 'color': 'green'},
            2: {'label': 'Razoável', 'color': 'yellow'},
            3: {'label': 'Moderada', 'color': 'orange'},
            4: {'label': 'Ruim', 'color': 'red'},
            5: {'label': 'Muito Ruim', 'color': 'purple'}
        }
        return aqi_labels.get(aqi)
    return None

def get_location_by_city(city):
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'limit': 1
    }
    
    response = requests.get('http://api.openweathermap.org/geo/1.0/direct', params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return {
                'lat': data[0]['lat'],
                'lon': data[0]['lon']
            }
    return None

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    city = data.get('city')
    
    if city:
        location = get_location_by_city(city)
        if location:
            lat = location['lat']
            lon = location['lon']
    
    if lat and lon:
        current = get_current_weather(lat, lon)
        forecast = get_forecast(lat, lon)
        air_quality = get_air_quality(lat, lon)
        
        if current and forecast:
            return jsonify({
                'current': current,
                'forecast': forecast,
                'air_quality': air_quality
            })
    
    return jsonify({'error': 'Cidade não encontrada'}), 404

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)