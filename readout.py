#!/usr/bin/python3

#
# this is a teeny webserver running in bottle, and a daemon framework that 
# performs periodic monitoring of whatever systems I feel are worth watching.
#

from bottle import route, run, template
import datetime, pytz

# the main page; shows a list of red/green icons, depending on whether the 
# service passed muster last time it was checked. If there were notes left
# by the monitor daemons, they will be printed following the status icons
@route('/')
def index():
    
    response
