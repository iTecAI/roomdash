var WEATHER = {};
var EVENTS = [];
var CONFIG = {};

var UNITS = {
    standard: "K",
    metric: "C",
    imperial: "F"
};
var WEEKDAYS = ['Sun.', 'Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.'];

function refresh_weather(data) {
    WEATHER = data;

    $('.radar').attr('src', '/data/weatherMap?'+Math.random());
    var dummy_stats = $('<div class="current-weather-stats"></div>');
    dummy_stats.append(
        $('<span class="weather-basic item"></span>')
            .append($('<img>').attr('src', 'http://openweathermap.org/img/wn/'+WEATHER.current.weather[0].icon+'@2x.png'))
            .append($('<span class="main"></span>').text(WEATHER.current.weather[0].main))
            .append($('<span class="desc"></span>').text('[ ' + WEATHER.current.weather[0].description.toUpperCase() + ' ]'))
    );
    dummy_stats.append(
        $('<span class="temperature item"></span>')
            .append($('<span class="material-icons">thermostat</span>'))
            .append($('<span class="main"></span>').text(WEATHER.current.temp + ' ' + UNITS[CONFIG.units]))
            .append($('<span class="desc"></span>').text('[ FEELS LIKE ' + WEATHER.current.feels_like + ' ' + UNITS[CONFIG.units] + ' ]'))
    );

    if (WEATHER.current.humidity < 30) {
        var humidityMeaning = '[ LOW HUMIDITY ]';
    } else if (WEATHER.current.humidity < 55) {
        var humidityMeaning = '[ OPTIMAL HUMIDITY ]';
    } else {
        var humidityMeaning = '[ HIGH HUMIDITY ]';
    }
    dummy_stats.append(
        $('<span class="humidity item"></span>')
            .append($('<span class="material-icons">water_drop</span>'))
            .append($('<span class="main"></span>').text(WEATHER.current.humidity + '%'))
            .append($('<span class="desc"></span>').text(humidityMeaning))
    );

    var uvi = WEATHER.current.uvi;
    if (uvi < 3) {
        var uvim = '[ LOW UVI ]';
    } else if (uvi < 6) {
        var uvim = '[ MODERATE UVI ]';
    } else if (uvi < 8) {
        var uvim = '[ HIGH UVI ]';
    } else if (uvi < 11) {
        var uvim = '[ VERY HIGH UVI ]';
    } else {
        var uvim = '[ EXTREME UVI ]';
    }
    dummy_stats.append(
        $('<span class="uvi item"></span>')
            .append($('<span class="material-icons">wb_sunny</span>'))
            .append($('<span class="main"></span>').text(WEATHER.current.uvi))
            .append($('<span class="desc"></span>').text(uvim))
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
                    .append($('<img>').attr('src', 'http://openweathermap.org/img/wn/'+WEATHER.hourly[h].weather[0].icon+'@2x.png'))
                    .append($('<span></span>').text(tm))
            );
    }
    hourly_weather.replaceAll('.weather-hourly')

    dummy_stats.replaceAll('.current-weather-stats');

    var dummy_daily = $('<div class="weather-daily"></div>');
    for (var d = 0; d < 8; d++) {
        var forecast = $('<div class="item"></div>');
        forecast.append(
            $('<img>').attr('src', 'http://openweathermap.org/img/wn/'+WEATHER.daily[d].weather[0].icon+'@2x.png')
        );
        var fore_date = new Date(WEATHER.daily[d].dt * 1000);
        forecast.append($('<span class="date"></span>').text(WEEKDAYS[fore_date.getDay()] + ' ' + fore_date.getMonth() + '/' + fore_date.getDate()));
        forecast
            .append(
                $('<div class="forecast-temp"></div>')
                    .append('<span class="material-icons">thermostat</span>')
                    .append($('<span class="value"><span>').text(WEATHER.daily[d].temp.min.toFixed(2) + ' ' + UNITS[CONFIG.units] + ' / ' + WEATHER.daily[d].temp.max.toFixed(2) + ' ' + UNITS[CONFIG.units]))
            )
            .append(
                $('<div class="forecast-humidity"></div>')
                    .append('<span class="material-icons">water_drop</span>')
                    .append($('<span class="value"><span>').text(WEATHER.daily[d].humidity + '%'))
            );
        var uvi = WEATHER.daily[d].uvi;
        if (uvi < 3) {
            var uvim = '[ LOW UVI ]';
        } else if (uvi < 6) {
            var uvim = '[ MODERATE UVI ]';
        } else if (uvi < 8) {
            var uvim = '[ HIGH UVI ]';
        } else if (uvi < 11) {
            var uvim = '[ VERY HIGH UVI ]';
        } else {
            var uvim = '[ EXTREME UVI ]';
        }
        forecast.append(
            $('<div class="forecast-uvi"></div>')
                .append('<span class="material-icons">wb_sunny</span>')
                .append($('<span class="value"><span>').text(uvi.toFixed(2) + ' ' + uvim))
        );
        dummy_daily.append(forecast);
    }
    dummy_daily.replaceAll('.weather-daily');
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