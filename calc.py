"""
ACP Brevet Time Calculator flask app
@author H. Keith Hamm
@date: Fall 2015

"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify  # For AJAX transactions
from flask import flash

import json
import logging

# Date handling
import arrow  # Replacement for datetime, based on moment.js
import datetime  # But we still need time
from dateutil import tz  # For interpreting local times
import CONFIG
import uuid
import re

# Our own module
# import acp_limits

# Globals
app = flask.Flask(__name__)
app.secret_key = str(uuid.uuid4())
app.debug = CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)

DEFAULT_DATE_TIME = arrow.get(arrow.now().replace(days=+1))

messages = []


# Pages
@app.route("/")
@app.route("/index")
@app.route("/calc")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found:\n {}".format(error))
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('page_not_found.html'), 404


# AJAX request handlers. These return JSON, rather than rendering pages.
@app.route("/_calc_date_times")
def calc_times():
    """
    Calculates open/close times from kilometers, using rules
    described at http://www.rusa.org/octime_alg.html.
    :return: A json object with the open and close times.
    """
    app.logger.debug("Got a JSON request")

    data = {'distance': request.args.get('distance', 0, type=int),
            'start_date': request.args.get('startDate', 0, type=str),
            'start_time': request.args.get('startTime', 0, type=str),
            'checkpoint': request.args.get('checkpoint', 0, type=int),
            'units': request.args.get('units', 0, type=str),
            'dates': request.args.get('dates', 0, type=str)}

    if data['units'] == 'miles':
        conv_fac = 0.621371
        data['distance'] /= conv_fac

    dates = data['dates']
    distance = data['distance']
    distance_max = data['distance'] + (data['distance'] * 0.2)
    distance_max_10 = data['distance'] + (data['distance'] * 0.1)
    checkpoint = data['checkpoint']
    is_valid_checkpoint = True
    is_over_10p = False

    if int(checkpoint) > distance_max:
        is_valid_checkpoint = False

    if int(checkpoint) > distance_max_10:
        is_over_10p = True

    if is_valid_checkpoint:
        data['checkpoint'] = int(data['checkpoint'])
        if data['start_date'] == '':
            data['start_date'] = DEFAULT_DATE_TIME.format('YYYY/MM/DD')

        if data['start_time'] == '':
            data['start_time'] = DEFAULT_DATE_TIME.format('12:00')

        open_time = get_date_time(data, 'max', 'open').format(
            dates + ' HH:mm')
        close_time = get_date_time(data, 'min', 'close').format(
            dates + ' HH:mm')

        start_date = data['start_date']
        start_time = data['start_time']

        start_open_date = arrow.get(start_date, 'YYYY/MM/DD').format(dates)

        start_close_time = arrow.get(start_time, 'HH:mm').replace(
            hours=+1).format('HH:mm')
    else:
        open_time = ''
        close_time = ''
        start_date = ''
        start_time = ''
        start_open_date = ''
        start_close_time = ''

    return jsonify(open_time=open_time, close_time=close_time,
                   start_date=start_date, start_time=start_time,
                   start_close_time=start_close_time,
                   start_open_date=start_open_date,
                   is_valid_checkpoint=is_valid_checkpoint,
                   is_over_10p=is_over_10p)


@app.route("/_get_start_date_times")
def get_start_date_times():
    """
    Gets the starting date and time.
    :return: A json object of the times.
    """
    start_date = request.args.get('startDate', 0, type=str)
    start_time = request.args.get('startTime', 0, type=str)

    is_valid_date = True
    if start_date == '':
        start_date = DEFAULT_DATE_TIME.format('YYYY/MM/DD')
    else:
        pattern = re.compile('[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]')
        if not pattern.match(start_date):
            is_valid_date = False

    is_valid_time = True
    if start_time == '':
        start_time = DEFAULT_DATE_TIME.format('12:00')
    else:
        pattern = re.compile('[0-9][0-9]:[0-9][0-9]')
        if not pattern.match(start_time):
            is_valid_time = False

    if is_valid_date and is_valid_time:
        start_close_time = arrow.get(start_time, 'HH:mm').replace(
            hours=+1).format('HH:mm')
    else:
        start_close_time = ''

    return jsonify(is_valid_date=is_valid_date,
                   is_valid_time=is_valid_time, start_time=start_time,
                   start_date=start_date,  start_close_time=start_close_time)


@app.route("/text")
def open_text():
    """
    Opens the times text document in the browser.
    :return: The times text document.
    """
    app.logger.debug("Getting text")
    return flask.send_from_directory('templates', 'times.txt')


@app.route("/_create_text")
def create_text():
    """
    Creates the times text document.
    :return: A json object.
    """
    app.logger.debug("Creating times text")
    brevet_distance = request.args.get('brevetDistance', 0, type=int)
    start_date = request.args.get('startDate', 0, type=str)
    start_time = request.args.get('startTime', 0, type=str)
    start_open = request.args.get('startOpen', 0, type=str)
    start_close = request.args.get('startClose', 0, type=str)
    units = request.args.get('units', 0, type=str)
    dates = request.args.get('dates', 0, type=str)
    checkpoint_distances = json.loads(request.args.get('checkpointDistances',
                                                       0, type=str))
    open_times = json.loads(request.args.get('openTimes', 0, type=str))
    close_times = json.loads(request.args.get('closeTimes', 0, type=str))

    unit = 'km'
    if units == 'miles':
        unit = 'mi'

    f = open('templates/times.txt', 'w')

    f.write('{}km BREVET\n'.format(brevet_distance))
    f.write('Checkpoint       Date  Time \n')
    f.write('==========       ===== =====\n')
    f.write('    0{}   start: {}\n'.format(unit, start_open))
    f.write('          close: {}\n'.format(start_close))
    f.write('                                  \n')

    for dist in checkpoint_distances:
        dist = str(dist)
        i = checkpoint_distances.index(dist)
        open_time = open_times[i]
        close_time = close_times[i]
        length = len(dist)
        if length == 1:
            space = '    '
        elif length == 2:
            space = '   '
        elif length == 3:
            space = '  '
        elif length == 4:
            space = ' '
        else:
            space = ''
        f.write('{}{}    open: {}\n'.format(space + dist, unit, open_time))
        f.write('          close: {}\n'.format(close_time))
        f.write('                                  \n')

    f.close()

    success = 'success'

    return jsonify(success=success)


# Other Functions
def get_date_time(data, speed, time_type):
    """
    Calculates and returns an arrow datetime for a checkpoint's open or close
    time.

    A checkpoint's open or close time is the sum of those portions of a
    checkpoint's distance from the starting point that fall within a series of
    ranges. Each range increment has a corresponding minimum and maximum speed.

    Rules:
    1) Determine what range increment the current distance falls within. Note
    the min and max speeds and the low end of the range increment.
    2) For open times: total += (current distance - low end) / max speed
    3) For close times: total += (current distance - low end) / min speed
    4) Set current distance -= (current distance - low end)
    5) Repeat 1 - 4 until current distance is 0
    6) Convert total into hours and minutes
    7) Add hours and minutes to the starting datetime

    Final checkpoint closing times in hours after start time:
    - 200 km: 13H30
    - 300 km: 20H00
    - 400 km: 27H00
    - 600 km: 40H00
    - 1000 km: 75H00

    :param data: speeds, distance, checkpoint, start_date, start_time
    :param speed: key into the speeds dict
    :param time_type: either open or close
    :return: an arrow datetime
    """
    distance = data['distance']
    distance_max = distance + (distance * 0.2)
    checkpoint = data['checkpoint']
    start_date = data['start_date']
    start_time = data['start_time']

    times = {200: {'open': {'hours': 5, 'min': 53},
                   'close': {'hours': 13, 'min': 30}},
             300: {'open': {'hours': 9, 'min': 0},
                   'close': {'hours': 20, 'min': 0}},
             400: {'open': {'hours': 12, 'min': 8},
                   'close': {'hours': 27, 'min': 0}},
             600: {'open': {'hours': 18, 'min': 48},
                   'close': {'hours': 40, 'min': 0}},
             1000: {'open': {'hours': 33, 'min': 5},
                    'close': {'hours': 75, 'min': 0}}}

    speeds = {'200': {'low': 0, 'min': 15, 'max': 34},
              '300': {'low': 200, 'min': 15, 'max': 32},
              '400': {'low': 200, 'min': 15, 'max': 32},
              '600': {'low': 400, 'min': 15, 'max': 30},
              '1000': {'low': 600, 'min': 11.428, 'max': 28},
              '1300': {'low': 1000, 'min': 13.333, 'max': 26}}

    is_final = False

    for time in times:
        if distance == int(time):
            is_final = True

    if is_final and distance <= checkpoint <= distance_max:
        hours = times[distance][time_type]['hours']
        mins = times[distance][time_type]['min']
        print('{}H{}'.format(hours, mins))
    else:
        total = 0

        while checkpoint:
            for dist in speeds:
                if speeds[dist]['low'] < checkpoint <= int(dist):
                    tmp = checkpoint - speeds[dist]['low']
                    if dist != '200':
                        checkpoint -= tmp
                    else:
                        checkpoint = 0
                    total += tmp / speeds[dist][speed]
                    break

        hours = int(total)
        mins = round((total - hours) * 60)

    tmp_time = "{} {}".format(start_date, start_time)
    date_time = arrow.get(tmp_time, 'YYYY/M/D HH:mm').replace(hours=+hours,
                                                              minutes=+mins)
    return date_time


if __name__ == "__main__":
    import uuid

    app.secret_key = str(uuid.uuid4())
    app.debug = CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)