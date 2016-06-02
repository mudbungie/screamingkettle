#!/usr/bin/env python3

from bottle import route, run, template
import datetime, pytz

from Database import *

def getStatuses():
    # Sort by status, and when that status last changed.
    s = Session()
    services = s.query(Service).all()
    services.sort(key=lambda service: service.currentStatus.observed)
    good = []
    bad = []
    for service in services:
        if service.currentStatus.good == True:
            good.append(service)
        else:
            bad.append(service)
    return bad + good

@route('/')
def index():
    response =  '<head><meta http-equiv="refresh" content="60">' +\
    '<style>' +\
    'td{border: 1px solid black;}' +\
    'td.good{background:green}' +\
    'td.bad{background:red}' +\
    '</style>' +\
    '</head>' +\
    '<body>' +\
    '<table>' +\
    '<tr><td>Service</td><td>Type</td><td>Status</td><td>Last Updated</td>' +\
    '<td>Status Unchanged For</td></tr>'
    response.append(getStatuses)
