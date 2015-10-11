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

# Our own module
# import acp_limits

# Globals
app = flask.Flask(__name__)

app.secret_key = str(uuid.uuid4())
app.debug = CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)

DEFAULT_DATE_TIME = arrow.get(arrow.now().replace(days=+1).format(
    'YYYY/MM/DD 12:00'), 'YYYY/MM/DD HH:mm')

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
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('page_not_found.html'), 404


# @app.route("/static/")


# AJAX request handlers. These return JSON, rather than rendering pages.
@app.route("/_calc_date_times")
def calc_times():
    """
    Calculates open/close times from miles, using rules
    described at http://www.rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of kilometers.
    """
    app.logger.debug("Got a JSON request")

    data = {'distance': request.args.get('distance', 0, type=int),
            'start_date': request.args.get('startDate', 0, type=str),
            'start_time': request.args.get('startTime', 0, type=str),
            'checkpoint': request.args.get('checkpoint', 0, type=int),
            'speeds': {
                '200': {'min': 15, 'max': 34},
                '400': {'min': 15, 'max': 32},
                '600': {'min': 15, 'max': 30},
                '1000': {'min': 11.428, 'max': 28},
                '1300': {'min': 13.333, 'max': 26},
            }}

    if data['start_date'] == '' or data['start_time'] == '':
        if data['start_date'] == '' and data['start_time'] == '':
            data['start_date'] = DEFAULT_DATE_TIME.format('YYYY/MM/DD')
            data['start_time'] = DEFAULT_DATE_TIME.format('HH:mm')
        elif data['start_date'] == '':
            data['start_date'] = DEFAULT_DATE_TIME.format('YYYY/MM/DD')
        elif data['start_time'] == '':
            data['start_time'] = DEFAULT_DATE_TIME.format('HH:mm')

    print('start: {} {}'.format(data['start_date'], data['start_time']))

    open_time = get_date_time(data, 'max')
    close_time = get_date_time(data, 'min')

    if open_time == data['checkpoint']:
        open_time = 'Error'
    if close_time == data['checkpoint']:
        close_time = 'Error'

    start_date = data['start_date']
    start_time = data['start_time']

    start_close_time = arrow.get(start_time, 'HH:mm').replace(hours=+1).format(
        'HH:mm')

    return jsonify(open_time=open_time, close_time=close_time,
                   start_date=start_date, start_time=start_time,
                   start_close_time=start_close_time)


@app.route("/_get_start_date_times")
def get_start_date_times():
    start_date = request.args.get('startDate', 0, type=str)
    start_time = request.args.get('startTime', 0, type=str)

    if start_date == '':
        start_time = DEFAULT_DATE_TIME.format('YYYY/MM/DD')

    if start_time == '':
        start_time = DEFAULT_DATE_TIME.format('HH:mm')

    start_close_time = arrow.get(start_time, 'HH:mm').replace(hours=+1).format(
        'HH:mm')

    return jsonify(start_time=start_time, start_date=start_date,
                   start_close_time=start_close_time)


# Other Functions
def get_date_time(data, speed):
    speeds = data['speeds']
    distance = data['distance']
    checkpoint = data['checkpoint']
    start_date = data['start_date']
    start_time = data['start_time']

    # TODO handle other distances

    if distance <= 200:
        total = checkpoint / speeds['200'][speed]
        hours = int(total)
        mins = int((total - hours) * 60)
        time = "{} {}".format(start_date, start_time)

        date_time = arrow.get(time, 'YYYY/M/D HH:mm').replace(hours=+hours,
                                                              minutes=+mins)
        return date_time.format('YYYY/MM/DD HH:mm')


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
