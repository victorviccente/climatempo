// static/js/weather.js

// DOM Elements
const elements = {
    citySearch: document.getElementById('citySearch'),
    searchBtn: document.getElementById('searchBtn'),
    locationBtn: document.getElementById('locationBtn'),
    themeToggle: document.getElementById('themeToggle'),
    loadingState: document.getElementById('loadingState'),
    weatherContent: document.getElementById('weatherContent'),
    errorMessage: document.getElementById('errorMessage'),
    // Weather info elements
    location: document.getElementById('location'),
    description: document.getElementById('description'),
    datetime: document.getElementById('datetime'),
    temperature: document.getElementById('temperature'),
    feelsLike: document.getElementById('feelsLike'),
    sunrise: document.getElementById('sunrise'),
    sunset: document.getElementById('sunset'),
    windSpeed: document.getElementById('windSpeed'),
    humidity: document.getElementById('humidity'),
    airQualityValue: document.getElementById('airQualityValue'),
    forecast: document.getElementById('forecast')
};

// Theme Management
let isDarkMode = false;

function toggleTheme() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('theme-dark', isDarkMode);
    document.body.classList.toggle('theme-light', !isDarkMode);
    elements.themeToggle.innerHTML = `<i class="fas fa-${isDarkMode ? 'sun' : 'moon'}"></i>`;
}

// Weather Icons
const weatherIcons = {
    sun: 'fa-sun',
    moon: 'fa-moon',
    'cloud-sun': 'fa-cloud-sun',
    'cloud-moon': 'fa-cloud-moon',
    cloud: 'fa-cloud',
    clouds: 'fa-clouds',
    'cloud-rain': 'fa-cloud-rain',
    'cloud-sun-rain': 'fa-cloud-sun-rain',
    'cloud-moon-rain': 'fa-cloud-moon-rain',
    'cloud-lightning': 'fa-bolt',
    snowflake: 'fa-snowflake',
    'cloud-fog': 'fa-smog',
    question: 'fa-question'
};

// Show/Hide Loading State
function toggleLoading(show) {
    elements.loadingState.classList.toggle('hidden', !show);
    elements.weatherContent.classList.toggle('hidden', show);
    elements.errorMessage.classList.toggle('hidden', true);
}

// Error Handling
function showError(message) {
    elements.errorMessage.querySelector('p').textContent = message;
    elements.errorMessage.classList.remove('hidden');
    elements.weatherContent.classList.add('hidden');
    elements.loadingState.classList.add('hidden');
}

// Update Weather UI
function updateWeatherUI(data) {
    if (!data.current) return;

    const current = data.current;
    
    // Update location and basic info
    elements.location.textContent = `${current.city}, ${current.country}`;
    elements.description.textContent = current.description;
    elements.datetime.textContent = new Date().toLocaleDateString('pt-BR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    // Update main temperature
    elements.temperature.textContent = `${current.temp}`;
    elements.feelsLike.textContent = `Sensação térmica: ${current.feels_like}°C`;
    
    // Update additional info
    elements.sunrise.textContent = current.sunrise;
    elements.sunset.textContent = current.sunset;
    elements.windSpeed.textContent = `${current.wind_speed} km/h`;
    elements.humidity.textContent = `${current.humidity}%`;

    // Update air quality if available
    if (data.air_quality) {
        elements.airQualityValue.textContent = data.air_quality.label;
        elements.airQualityValue.style.color = data.air_quality.color;
    }

    // Update forecast
    updateForecast(data.forecast);
}

// Update Forecast UI
function updateForecast(forecast) {
    elements.forecast.innerHTML = forecast.map(day => `
        <div class="bg-[var(--card-bg)] backdrop-blur-md rounded-xl p-4 text-center weather-card">
            <h4 class="font-semibold">${day.day_name}</h4>
            <p class="text-sm opacity-75">${day.date}</p>
            <i class="fas ${weatherIcons[day.icon]} text-3xl my-3"></i>
            <p class="text-sm">${day.description}</p>
            <div class="flex justify-around mt-2">
                <span>${day.temp_max}°</span>
                <span class="opacity-75">${day.temp_min}°</span>
            </div>
        </div>
    `).join('');
}

// Fetch Weather Data
async function fetchWeather(params) {
    try {
        toggleLoading(true);
        
        const response = await fetch('/weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });

        const data = await response.json();

        if (!response.ok) throw new Error(data.error || 'Erro ao buscar dados do clima');

        updateWeatherUI(data);
        elements.weatherContent.classList.remove('hidden');
    } catch (error) {
        showError(error.message);
    } finally {
        toggleLoading(false);
    }
}

// Geolocation
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                fetchWeather({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                });
            },
            error => {
                showError('Erro ao obter localização. Por favor, digite uma cidade.');
            }
        );
    } else {
        showError('Geolocalização não suportada pelo seu navegador.');
    }
}

// Event Listeners
elements.themeToggle.addEventListener('click', toggleTheme);
elements.locationBtn.addEventListener('click', getLocation);

elements.searchBtn.addEventListener('click', () => {
    const city = elements.citySearch.value.trim();
    if (city) {
        fetchWeather({ city });
    }
});

elements.citySearch.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const city = elements.citySearch.value.trim();
        if (city) {
            fetchWeather({ city });
        }
    }
});

// Initialize app with user's location
getLocation();