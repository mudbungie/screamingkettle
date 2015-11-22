#!/usr/bin/python3

# the main page; shows a list of red/green icons, depending on whether the 
# service passed muster last time it was checked. If there were notes left
# by the monitor daemons, they will be printed following the status icons

from bottle import route, run, template
import datetime, pytz
import os.path
import monitorStatus

@route('/')
def index():
    statuses = []
    response =  '<body>\n'
    response += '<table>\n'
    response += '<tr><td>Service</td><td>Status</td><td>Notes</td></tr>\n'
    # for adding each status to the table
    def appendStatus(fieldName):
        try:
            row =  '<td>' + fieldName + '</td>'
        # to keep things aligned in case a field is empty
        except KeyError:
            row =  '<td></td><td></td>'
        return row
    # crawl the statuses directory for all the things that I'm watching
    for listing in os.listdir(monitorStatus.statusFilesPath):
        a = monitorStatus.recordedStatus(listing)
        statuses.append(a)
    # add the contents of those statuses to the response 
    for status in statuses:
        response += '<tr>'
        response += '<td>' + status.values['service'] + '</td>'
        response += '<td>' + status.values['status'] + '</td>'
        response += '<td>' + status.values['notes'] + '</td>'
        response += '</tr>\n'

    response += '</table>\n'
    response += '</body>'
    return response

run(host='0.0.0.0', port=8000)
