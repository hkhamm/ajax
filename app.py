"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify # For AJAX transactions
from flask import flash

import json
import logging

# Date handling
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
# import acp_limits

# Globals
app = flask.Flask(__name__)
import CONFIG

import uuid
app.secret_key = str(uuid.uuid4())
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)

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


# AJAX request handlers. These return JSON, rather than rendering pages.
@app.route("/_calc_times")
def calc_times():
    """
    Calculates open/close times from miles, using rules
    described at http://www.rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of kilometers.
    """
    app.logger.debug("Got a JSON request");

    data = {}
    data['distance'] = request.args.get('distance', 0, type=int)
    data['start_time'] = request.args.get('start_time', 0, type=str)
    data['start_date'] = request.args.get('start_date', 0, type=str)
    data['checkpoint'] = request.args.get('checkpoint', 0, type=int)
    data['speeds'] = {
      '200': {'min': 15, 'max': 34},
      '400': {'min': 15, 'max': 32},
      '600': {'min': 15, 'max': 30},
      '1000': {'min': 11.428, 'max': 28},
      '1300': {'min': 13.333, 'max': 26},
    }

    open_time = get_datetime(data, 'max')
    close_time = get_datetime(data, 'min')

    if open_time == data['checkpoint']:
        open_time = 'Error'
    if close_time == data['checkpoint']:
        close_time = 'Error'

    return jsonify(open_time=open_time, close_time=close_time)


# Other Functions
def get_datetime(data, speed):
    speeds = data['speeds']
    distance = data['distance']
    checkpoint = data['checkpoint']
    start_date = data['start_date']
    start_time = data['start_time']

    # TODO handle other distances

    if distance <= 200:
        total = checkpoint/speeds['200'][speed]
        hours = int(total)
        mins = int((total - hours) * 60)
        time = "{} {}".format(start_date, start_time)
        datetime = arrow.get(time, 'YYYY/M/D HH:mm').replace(hours=+hours,
                                                             minutes=+mins)
        return datetime.format('YYYY/MM/DD HH:mm')


# Functions used within the templates
@app.template_filter('fmttime')
def format_arrow_time(time):
    try:
        normal = arrow.get( date )
        return normal.format("hh:mm")
    except:
        return "(bad time)"


@app.template_filter('fmtdate')
def format_arrow_date(date):
    try:
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"


if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)
