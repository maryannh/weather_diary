from flask import Flask, render_template, redirect, session, flash, request, jsonify, url_for, Blueprint
import requests
from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta, date
import calendar
import pprint

app = Flask(__name__)
app.config.from_pyfile('settings.py')
pp = pprint.PrettyPrinter(indent=4)

bootstrap = Bootstrap(app) 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/<monthyear>")
def weather(monthyear):
    month = monthyear[:2]
    month_name = calendar.month_name[int(month)]
    year = monthyear[-4:]
    api_key = app.config["DARKSKY"]
    latitude = str(app.config["LAT"])
    longitude = str(app.config["LONG"])
    payload = {'exclude': 'currently,minutely,hourly,alerts,flags', 'units': 'uk2'}
    days = calendar.monthrange(int(year), int(month))
    filler_days = 7
    days_in_month = days[1]
    final_week = days_in_month-28
    filler_days = 7-final_week
    weather_chart = []
    total_max_temp = 0
    total_min_temp = 0
    for i in range(days_in_month):
        day = str(i+1).zfill(2)
        date = year + "-" + month + "-" + day + "T12:00:00Z"
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        api_url = "https://api.darksky.net/forecast/" + api_key + "/" + latitude + "," + longitude + "," + date
        r = requests.get(api_url, params=payload)
        data = r.json()
        day_name = dt.strftime("%A")
        max_temp = round(data["daily"]["data"][0]["temperatureMax"])
        min_temp = round(data["daily"]["data"][0]["temperatureMin"])
        summary = None
        if "summary" in data["daily"]["data"][0]:
            summary = data["daily"]["data"][0]["summary"]
        hot = False
        if int(max_temp) >= 25:
            hot = True
        freezing = False
        if int(min_temp) <= 0:
            freezing = True
        info = {
                "day": str(i+1),
                "day_name": day_name,
                "month_name": month_name,
                "year": year,
                "summary": summary,
                "max_temp": max_temp,
                "min_temp": min_temp,
                "hot": hot,
                "freezing": freezing,
            }
        db.weather.insert_one(info)
        weather_chart.append(info)
        # total_max_temp = total_max_temp + max_temp
        # mean_max_temp = total_max_temp / days_in_month
        # total_min_temp = total_min_temp + min_temp
        # mean_max_temp = total_min_temp / days_in_month
    return render_template("weather.html", year=year, weather_chart=weather_chart, month_name=month_name, filler_days=filler_days)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="4565")