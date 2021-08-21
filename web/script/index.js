var WEATHER = {};
var EVENTS = [];
var CONFIG = {};
var FSSET = false;

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
            //.append($('<span class="main"></span>').text(WEATHER.current.weather[0].main))
            //.append($('<span class="desc"></span>').text('[ ' + WEATHER.current.weather[0].description.toUpperCase() + ' ]'))
    );
    dummy_stats.append(
        $('<span class="temperature item"></span>')
            .append($('<span class="material-icons">thermostat</span>'))
            .append($('<span class="main"></span>').text(Math.round(WEATHER.current.temp) + '°' + UNITS[CONFIG.units]))
            .append($('<span class="desc"></span>').text('[ ' + Math.round(WEATHER.current.feels_like) + '°' + UNITS[CONFIG.units] + ' ]'))
    );

    if (WEATHER.current.humidity < 30) {
        var humidityMeaning = '[ LOW ]';
    } else if (WEATHER.current.humidity < 55) {
        var humidityMeaning = '[ GOOD ]';
    } else {
        var humidityMeaning = '[ HIGH ]';
    }
    dummy_stats.append(
        $('<span class="humidity item"></span>')
            .append($('<span class="material-icons">water_drop</span>'))
            .append($('<span class="main"></span>').text(WEATHER.current.humidity + '%'))
            .append($('<span class="desc"></span>').text(humidityMeaning))
    );

    var uvi = WEATHER.current.uvi;
    if (uvi < 3) {
        var uvim = '[ LOW ]';
    } else if (uvi < 6) {
        var uvim = '[ MED ]';
    } else if (uvi < 8) {
        var uvim = '[ HIGH ]';
    } else if (uvi < 11) {
        var uvim = '[ HIGH+ ]';
    } else {
        var uvim = '[ MEGA ]';
    }
    dummy_stats.append(
        $('<span class="uvi item"></span>')
            .append($('<span class="material-icons">wb_sunny</span>'))
            .append($('<span class="main"></span>').text(WEATHER.current.uvi))
            .append($('<span class="desc"></span>').text(uvim))
    );

    var hourly_weather = $('<div class="weather-hourly"></div>');
    var item_count = Math.floor($('.weather-hourly').width() / 64);
    if (item_count > 16) {
        item_count = 16;
    }
    var item_width = Math.ceil($('.weather-hourly').width() / item_count) - 10;
    console.log(item_count, item_width);
    for (var h = 0; h <= item_count * 2 - 1; h += 2) {
        var d = new Date(WEATHER.hourly[h].dt * 1000);
        if (d.getHours() > 12) {
            var hstring = d.getHours() - 12;
            var suffix = 'PM';
        } else if (d.getHours() == 12) {
            var hstring = d.getHours();
            var suffix = 'PM';
        } else if (d.getHours() == 0) {
            var hstring = 12;
            var suffix = 'AM';
        } else {
            var hstring = d.getHours();
            var suffix = 'AM';
        }
        var tm = hstring + ' ' + suffix;
        hourly_weather
            .append(
                $('<div class="hourly-weather-item"></div>')
                    .append($('<img>').attr('src', 'http://openweathermap.org/img/wn/'+WEATHER.hourly[h].weather[0].icon+'@2x.png'))
                    .append($('<span></span>').text(tm))
                    .css('width', item_width+'px')
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
        forecast.append($('<span class="date"></span>').text(WEEKDAYS[fore_date.getDay()] + ' ' + (fore_date.getMonth() + 1) + '/' + (fore_date.getDate() + 1)));
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
        forecast.append(
            $('<div class="forecast-uvi"></div>')
                .append('<span class="material-icons">wb_sunny</span>')
                .append($('<span class="value"><span>').text(uvi.toFixed(2)))
        );
        dummy_daily.append(forecast);
    }
    dummy_daily.replaceAll('.weather-daily');
}

function zero(val, num) {
    while (val.toString().length < num) {
        val = '0' + val;
    }
    return val;
}

function refresh_events(data) {
    EVENTS = data;

    var dummy_events = $('<div class="events-area"></div>');
    for (var e of EVENTS) {
        var eventItem = $('<div class="event-item"></div>');
        eventItem.append(
            $('<span class="prop name"></span>')
                .append($('<span class="material-icons">event_note</span>'))
                .append($('<span class="value"></span>').text(e.name))
        );
        var start = {
            year: Number(e.start.split('T')[0].split('-')[0]),
            month: Number(e.start.split('T')[0].split('-')[1]),
            date: Number(e.start.split('T')[0].split('-')[2]),
            hour: Number(e.start.split('T')[1].split(':')[0]),
            minute: Number(e.start.split('T')[1].split(':')[1]),
            second: Number(e.start.split('T')[1].split(':')[2].split('+')[0].split('-')[0])
        };
        start = new Date(start.year, start.month, start.date, start.hour, start.minute, start.second);
        var end = {
            year: Number(e.end.split('T')[0].split('-')[0]),
            month: Number(e.end.split('T')[0].split('-')[1]),
            date: Number(e.end.split('T')[0].split('-')[2]),
            hour: Number(e.end.split('T')[1].split(':')[0]),
            minute: Number(e.end.split('T')[1].split(':')[1]),
            second: Number(e.end.split('T')[1].split(':')[2].split('+')[0].split('-')[0])
        };
        end = new Date(end.year, end.month, end.date, end.hour, end.minute, end.second);

        var start_str = zero(start.getMonth(), 2) + '/' + 
            zero(start.getDate(), 2) + '/' + 
            start.getFullYear() + ' ' +
            zero(start.getHours(), 2) + ':' +
            zero(start.getMinutes(), 2);
        var end_str = zero(end.getMonth(), 2) + '/' + 
            zero(end.getDate(), 2) + '/' + 
            end.getFullYear() + ' ' +
            zero(end.getHours(), 2) + ':' +
            zero(end.getMinutes(), 2);
        
        if (
            start.getHours() == 0 &&
            start.getMinutes() == 0 &&
            start.getSeconds() == 0 &&
            end.getHours() == 0 &&
            end.getMinutes() == 0 &&
            end.getSeconds() == 0
        ) {
            start_str = start_str.split(' ')[0];
            end_str = end_str.split(' ')[0];
        }

        eventItem.append(
            $('<span class="prop time"></span>')
                .append($('<span class="material-icons">schedule</span>'))
                .append($('<span class="value"></span>').text(start_str + ' - ' + end_str))
        );
        eventItem.append(
            $('<span class="prop creator"></span>')
                .append($('<span class="material-icons">person</span>'))
                .append($('<span class="value"></span>').text(e.creator))
        );
        eventItem.append(
            $('<span class="prop status"></span>')
                .append($('<span class="material-icons">info</span>'))
                .append($('<span class="value"></span>').text(e.status))
        );
        eventItem.append(
            $('<img>').attr('src', e.qrcode)
        );

        dummy_events.append(eventItem);
    }
    dummy_events.replaceAll('.events-area');
    $('.no-events').toggle(EVENTS.length == 0);
}

function refresh_time() {
    var now = new Date(Date.now());
    if (now.getHours() < 10) {
        var hrs = '0' + now.getHours();
    } else {
        var hrs = now.getHours();
    }
    if (now.getMinutes() < 10) {
        var min = '0' + now.getMinutes();
    } else {
        var min = now.getMinutes();
    }
    if (now.getSeconds() < 10) {
        var sec = '0' + now.getSeconds();
    } else {
        var sec = now.getSeconds();
    }
    $('#time-panel .time').text(hrs + ':' + min + ':' + sec);
    $('#time-panel .date').text(WEEKDAYS[now.getDay()] + ' ' + (now.getMonth() + 1) + '/' + (now.getDate() + 1) + '/' + now.getFullYear());
    $('#time-panel .location-name .value').text(CONFIG.target.locationDisplayName);
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