#!/usr/bin/python3

# the main page; shows a list of red/green icons, depending on whether the 
# service passed muster last time it was checked. If there were notes left
# by the monitor daemons, they will be printed following the status icons

from bottle import route, run, template
import datetime, pytz
import os.path
import status

@route('/')
def index():
    # crawl the 
    for statusFile in os.listdir('status'):
        with open()
    response
    return response

run(host='0.0.0.0', port=8000)
