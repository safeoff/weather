# encoding:utf-8
"""."""
import json
from datetime import datetime
import requests
import os


def loadData():
    api = os.environ['OPENWEATHERMAP_KEY']
    lonlat = [os.environ['LON'], os.environ['LAT']]
    b = 'http://api.openweathermap.org/data/2.5/forecast/?units=metric&lat='
    u = b + '{a}&lon={b}&APPID={c}'.format(a=lonlat[0], b=lonlat[1], c=api)
    r = requests.get(u)
    return json.loads(r.text)


class forecast:
    icon = ''

    def __init__(self):
        self.temp_max = 0
        self.temp_min = 100
        self.speed    = 0
        self.humidity = 0
        self.rain     = []
        self.snow     = []
        self.cloud    = 0
        self.time     = ''
        self.datetime = ''
        self.weather  = 'Clear'


def makeForecast(d):
    f = forecast()
    f.icon = ''
    a = []
    emoji = {'Clear': ':sunny:', 'Clouds': ':cloud:',
             'Rain': ':umbrella:', 'Snow': ':snowman:'}

    for x in d['list']:
        f.datetime = datetime.fromtimestamp(x['dt'])
        time = '{0:%H}'.format(f.datetime)
        if time == '00':
            f.__init__()

        classifyData(f, x)

        if time == '21':
            for i in f.snow:
                if i > 0.5:
                    f.weather = 'Snow'
            for i in f.rain:
                if i > 0.5:
                    f.weather = 'Rain'
            if f.icon == '':
                f.icon = emoji[f.weather]
                a.append(f.icon)
            a.append(formatForecast(f))

    a.append(formatForecast(f))

    return a


def formatForecast(f):
    wj = ('日', '月', '火', '水', '木', '金', '土')
    mj = {'Clear': '晴', 'Clouds': '曇', 'Rain': '雨', 'Snow': '雪'}

    s = '{0:%m%d}'.format(f.datetime) + wj[int('{0:%w}'.format(f.datetime))]
    s += '     ' + mj[f.weather]
    s += '   ↑' + str(round(f.temp_max))
    s += '   ↓' + str(round(f.temp_min))
    s += '   風' + str(round(f.speed / 10))
    s += '   湿' + str(round(f.humidity / 10))
    if f.weather == 'Rain' or f.weather == 'Snow':
        s += formatPrecipitation(f)

    return s


def formatPrecipitation(f):
    s = ''

    if formatPrecipitationCore(f.rain) != '':
        s += '\n     時' + f.time
        s += '\n     雨'
        s += formatPrecipitationCore(f.rain)

    if formatPrecipitationCore(f.snow) != '':
        s += '\n     時' + f.time
        s += '\n     雪'
        s += formatPrecipitationCore(f.snow)

    return s


def formatPrecipitationCore(rs):
    s = ''
    b = False

    for x in rs:
        if round(x) == 0:
            s += '       -  '
        else:
            s += '      ' + str(round(x)) + '   '
            b = True
    s = s.rstrip()

    if b is True:
        return s
    else:
        return ''


def classifyData(f, x):
    f.time     += '   {0:%H}'.format(datetime.fromtimestamp(x['dt']))
    f.speed    += x['wind']['speed']
    f.humidity += x['main']['humidity']
    if x['clouds']['all'] > 80:
        f.weather = 'Clouds'
    if f.temp_max < x['main']['temp_max']:
        f.temp_max = x['main']['temp_max']
    if f.temp_min > x['main']['temp_min']:
        f.temp_min = x['main']['temp_min']
    try:
        f.rain.append(x['rain']['3h'] / 3)
    except:
        f.rain.append(0)
    try:
        f.snow.append(x['snow']['3h'] / 3)
    except:
        f.snow.append(0)

    return f


def postSlack(a):
    e = a[0]
    s = formatStr(a)

    k = os.environ['WEBHOOK_KEY']
    u = 'https://hooks.slack.com/services/%s' % k
    j = {
        'text': s,
        'icon_emoji': e
    }
    requests.post(u, json.dumps(j))
    return


def formatStr(a):
    a.pop(0)
    s = ''
    for x in a:
        s += x + '\n'
    return s.rstrip('\n')


if __name__ == '__main__':
    d = loadData()
    a = makeForecast(d)
    postSlack(a)
