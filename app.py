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

# import json
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
    """
    app.logger.debug("Got a JSON request")

    data = {'distance': request.args.get('distance', 0, type=int),
            'start_date': request.args.get('startDate', 0, type=str),
            'start_time': request.args.get('startTime', 0, type=str),
            'checkpoint': request.args.get('checkpoint', 0, type=int),
            'speeds': {
                '200': {'low': 0, 'min': 15, 'max': 34},
                '400': {'low': 200, 'min': 15, 'max': 32},
                '600': {'low': 400, 'min': 15, 'max': 30},
                '1000': {'low': 600, 'min': 11.428, 'max': 28},
                '1300': {'low': 1000, 'min': 13.333, 'max': 26},
            }}

    # speeds = {'200': {'min': 15, 'max': 34},
    #           '400': {'min': 15, 'max': 32},
    #           '600': {'min': 15, 'max': 30},
    #           '1000': {'min': 11.428, 'max': 28},
    #           '1300': {'min': 13.333, 'max': 26}}

    # TODO validate checkpoint

    distance = data['distance']
    distance_max = data['distance'] + (data['distance'] * 0.1)
    pattern = re.compile('[0-9]*')
    checkpoint = data['checkpoint']
    speeds = data['speeds']
    low_speed = speeds[str(distance)]['low']
    is_valid_checkpoint = True

    if is_valid_checkpoint:
        if low_speed <= int(checkpoint) > distance_max:
            is_valid_checkpoint = False

    if is_valid_checkpoint:
        data['checkpoint'] = int(data['checkpoint'])
        if data['start_date'] == '':
            data['start_date'] = DEFAULT_DATE_TIME.format('YYYY/MM/DD')

        if data['start_time'] == '':
            data['start_time'] = DEFAULT_DATE_TIME.format('12:00')

        open_time = get_date_time(data, 'max', 'open').format(
            'YYYY/MM/DD HH:mm')
        close_time = get_date_time(data, 'min', 'close').format(
            'YYYY/MM/DD HH:mm')

        # if open_time == checkpoint:
        #     open_time = 'Error'
        # if close_time == checkpoint:
        #     close_time = 'Error'

        start_date = data['start_date']
        start_time = data['start_time']

        start_close_time = arrow.get(start_time, 'HH:mm').replace(
            hours=+1).format('HH:mm')
    else:
        open_time = ''
        close_time = ''
        start_date = ''
        start_time = ''
        start_close_time = ''

    return jsonify(open_time=open_time, close_time=close_time,
                   start_date=start_date, start_time=start_time,
                   start_close_time=start_close_time,
                   is_valid_checkpoint=is_valid_checkpoint)


@app.route("/_get_start_date_times")
def get_start_date_times():
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

    Final checkpoint closing times for 200 km and 400 km brevets:
    - 200 km: 13.5 hours rather than 13.33 hours
    - 400 km: 27 hours rather than 26.66 hours

    :param data: speeds, distance, checkpoint, start_date, start_time
    :param speed: key into the speeds dict
    :param time_type: either open or close
    :return: an arrow datetime
    """
    speeds = data['speeds']
    distance = data['distance']
    checkpoint = data['checkpoint']
    start_date = data['start_date']
    start_time = data['start_time']

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

    if data['checkpoint'] == 200 and time_type == 'close':
        mins = 30
    elif data['checkpoint'] == 400 and time_type == 'close':
        mins = 60
    else:
        mins = round((total - hours) * 60)

    tmp_time = "{} {}".format(start_date, start_time)
    date_time = arrow.get(tmp_time, 'YYYY/M/D HH:mm').replace(hours=+hours,
                                                              minutes=+mins)
    return date_time


def get_total(checkpoint, total, speeds, speed):
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
    if checkpoint:
        get_total(checkpoint, total, speeds, speed)

    return total


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
