"""
ACP Brevet Time Calculator flask app
@author H. Keith Hamm
@date: Fall 2015

"""

import flask
# from flask import render_template
from flask import request
# from flask import url_for
from flask import jsonify  # For AJAX transactions
# from flask import flash

import json
import logging

# Date handling
import arrow  # Replacement for datetime, based on moment.js
# import datetime  # But we still need time
# from dateutil import tz  # For interpreting local times
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
            'dates': request.args.get('dates', 0, type=str),
            'speeds': {
                '200': {'low': 0, 'min': 15, 'max': 34},
                '300': {'low': 200, 'min': 15, 'max': 32},
                '400': {'low': 200, 'min': 15, 'max': 32},
                '600': {'low': 400, 'min': 15, 'max': 30},
                '1000': {'low': 600, 'min': 11.428, 'max': 28},
                '1300': {'low': 1000, 'min': 13.333, 'max': 26},
            }}

    if data['units'] == 'miles':
        conv_fac = 0.621371
        data['distance'] /= conv_fac

    dates = data['dates']
    distance = data['distance']
    distance_max = data['distance'] + (data['distance'] * 0.2)
    checkpoint = data['checkpoint']
    speeds = data['speeds']
    # low_speed = speeds[str(distance)]['low']
    is_valid_checkpoint = True

    if int(checkpoint) > distance_max:
        is_valid_checkpoint = False

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
                   is_valid_checkpoint=is_valid_checkpoint)


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

    Final checkpoint closing times:
    - 200 km: 13.5 hours rather than 13.33 hours
    - 400 km: 27 hours rather than 26.66 hours

    :param data: speeds, distance, checkpoint, start_date, start_time
    :param speed: key into the speeds dict
    :param time_type: either open or close
    :return: an arrow datetime
    """
    speeds = data['speeds']
    distance = data['distance']
    distance_max = distance + (distance * 0.2)
    checkpoint = data['checkpoint']
    start_date = data['start_date']
    start_time = data['start_time']

    if distance == 200 and 200 <= checkpoint <= distance_max:
        if time_type == 'close':
            hours = 13
            mins = 30
        else:
            hours = 5
            mins = 53
    elif distance == 300 and 300 <= checkpoint <= distance_max:
        if time_type == 'close':
            hours = 20
            mins = 0
        else:
            hours = 9
            mins = 0
    elif distance == 400 and 400 <= checkpoint <= distance_max:
        if time_type == 'close':
            hours = 27
            mins = 0
        else:
            hours = 12
            mins = 8
    elif distance == 600 and 600 <= checkpoint <= distance_max:
        if time_type == 'close':
            hours = 40
            mins = 0
        else:
            hours = 18
            mins = 48
    elif distance == 1000 and 1000 <= checkpoint <= distance_max:
        if time_type == 'close':
            hours = 75
            mins = 0
        else:
            hours = 33
            mins = 5
    else:
        total = 0

        while checkpoint:
            if 0 < checkpoint <= 200:
                tmp = checkpoint
                checkpoint = 0
                total += tmp / speeds['200'][speed]
            elif 200 < checkpoint <= 400:
                tmp = checkpoint - 200
                checkpoint -= tmp
                total += tmp / speeds['400'][speed]
            elif 400 < checkpoint <= 600:
                tmp = checkpoint - 400
                checkpoint -= tmp
                total += tmp / speeds['600'][speed]
            elif 600 < checkpoint <= 1000:
                tmp = checkpoint - 600
                checkpoint -= tmp
                total += tmp / speeds['1000'][speed]
            elif 1000 < checkpoint <= 1300:
                tmp = checkpoint - 1000
                checkpoint -= tmp
                total += tmp / speeds['1300'][speed]

        hours = int(total)
        mins = round((total - hours) * 60)

    tmp_time = "{} {}".format(start_date, start_time)
    date_time = arrow.get(tmp_time, 'YYYY/M/D HH:mm').replace(hours=+hours,
                                                              minutes=+mins)
    return date_time


# def get_total(checkpoint, total, speeds, speed):
#     """
#     Calculates and returns the open and close times for a checkpoint.
#     :param checkpoint: The checkpoint to calculate times for.
#     :param total: The current total, used for recursion.
#     :param speeds: The speeds table (dict).
#     :param speed: The speed key into the table.
#     :return: The computed total hours from the starting checkpoint.
#     """
#     if 0 < checkpoint <= 200:
#         tmp = checkpoint
#         checkpoint = 0
#         total += tmp / speeds['200'][speed]
#     elif 200 < checkpoint <= 400:
#         tmp = checkpoint - 200
#         checkpoint -= tmp
#         total += tmp / speeds['400'][speed]
#     elif 400 < checkpoint <= 600:
#         tmp = checkpoint - 400
#         checkpoint -= tmp
#         total += tmp / speeds['600'][speed]
#     elif 600 < checkpoint <= 1000:
#         tmp = checkpoint - 600
#         checkpoint -= tmp
#         total += tmp / speeds['1000'][speed]
#     elif 1000 < checkpoint <= 1300:
#         tmp = checkpoint - 1000
#         checkpoint -= tmp
#         total += tmp / speeds['1300'][speed]
#     if checkpoint:
#         get_total(checkpoint, total, speeds, speed)
#
#     return total


# Functions used within the templates
# @app.template_filter('fmttime')
# def format_arrow_time(time):
#     try:
#         normal = arrow.get(date)
#         return normal.format("hh:mm")
#     except:
#         return "(bad time)"
#
#
# @app.template_filter('fmtdate')
# def format_arrow_date(date):
#     try:
#         normal = arrow.get(date)
#         return normal.format("ddd MM/DD/YYYY")
#     except:
#         return "(bad date)"


if __name__ == "__main__":
    import uuid

    app.secret_key = str(uuid.uuid4())
    app.debug = CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)
