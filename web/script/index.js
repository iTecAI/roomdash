var WEATHER = {};
var EVENTS = [];
var CONFIG = {};

var UNITS = {
    standard: "K",
    metric: "C",
    imperial: "F"
};
var SPEED_UNITS = {
    standard: "km/h",
    metric: "km/h",
    imperial: "mph"
};

function refresh_weather(data) {
    WEATHER = data;

    $('.radar').attr('src', '/data/weatherMap?'+Math.random());
    var dummy_stats = $('<div class="stats"></div>');
    dummy_stats.append(
        $('<span class="weather-basic"></span>')
            .append($('<img>').attr('src', 'http://openweathermap.org/img/wn/'+WEATHER.current.weather[0].icon+'.png'))
            .append($('<span></span>').text(WEATHER.current.weather[0].main + ' ('+WEATHER.current.weather[0].description+')'))
    );
    dummy_stats.append(
        $('<span class="temperature item"></span>')
            .append('<span class="material-icons">device_thermostat</span>')
            .append(
                $('<span></span>')
                    .text(WEATHER.current.temp + ' ' + UNITS[CONFIG.units] + ' (Feels like ' + WEATHER.current.feels_like + ' ' + UNITS[CONFIG.units] + ')')
            )
    );
    dummy_stats.append(
        $('<span class="humidity item"></span>')
            .append('<span class="material-icons">water_drop</span>')
            .append(
                $('<span></span>')
                    .text('Humidity: ' + WEATHER.current.humidity + '%')
            )
    );
    dummy_stats.append(
        $('<span class="wind item"></span>')
            .append('<span class="material-icons">air</span>')
            .append(
                $('<span></span>')
                    .text('Wind: ' + WEATHER.current.wind_speed + ' ' + SPEED_UNITS[CONFIG.units] + ' @ ' + WEATHER.current.wind_deg + ' deg.')
            )
    );
    dummy_stats.append(
        $('<span class="uvindex item"></span>')
            .append('<span class="material-icons">wb_sunny</span>')
            .append(
                $('<span></span>')
                    .text('UV Index: ' + WEATHER.current.uvi)
            )
    );

    var sunrise = new Date(WEATHER.current.sunrise*1000);
    var sunset = new Date(WEATHER.current.sunset*1000);
    var sun_fmt = 'Sunrise/Sunset: '+sunrise.getHours()+':'+sunrise.getMinutes()+' / '+sunset.getHours()+':'+sunset.getMinutes();
    
    dummy_stats.append(
        $('<span class="sunriseset item"></span>')
            .append('<span class="material-icons">brightness_6</span>')
            .append(
                $('<span></span>')
                    .text(sun_fmt)
            )
    );

    var hourly_weather = $('<div class="weather-hourly"></div>')
    for (var h = 0; h <= 16; h += 2) {
        var d = new Date(WEATHER.hourly[h].dt * 1000);
        if (d.getHours() > 12) {
            var hstring = d.getHours() - 12;
            var suffix = 'PM';
        } else {
            var hstring = d.getHours();
            var suffix = 'AM';
        }
        if (hstring == 0) {
            var tm = '12 AM';
        } else {
            var tm = hstring + ' ' + suffix;
        }
        hourly_weather
            .append(
                $('<div class="hourly-weather-item"></div>')
                    .append($('<img>').attr('src', 'http://openweathermap.org/img/wn/'+WEATHER.hourly[h].weather[0].icon+'.png'))
                    .append($('<span></span>').text(tm))
            );
    }
    dummy_stats.append(hourly_weather);

    dummy_stats.replaceAll('.current-weather-stats .stats');
}

function refresh_events(data) {
    EVENTS = data;
}

function refresh_time() {

}

$(document).ready(function () {
    $.get('/debug').done(function (data) {
        console.log('Loaded config');
        CONFIG = data;
        $.get('/data/weather').done(refresh_weather);
        $.get('/data/events').done(refresh_events);
        setInterval(function () {
            $.get('/data/weather').done(refresh_weather);
        }, 5000);
        setInterval(function () {
            $.get('/data/events').done(refresh_events);
        }, 5000);
        setInterval(refresh_time, 500);
    });
});