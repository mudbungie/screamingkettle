#!/usr/bin/python3

# The main page; shows a list of red/green icons, depending on whether the 
# service passed muster last time it was checked. If there were notes left
# by the monitor daemons, they will be printed following the status icons.

from bottle import route, run, template
import datetime, pytz
import os.path
import Kettles

def timeSince(timeString):
    startTime = datetime.datetime.strptime(timeString.replace(':',''),
                        '%Y-%m-%dT%H%M%S.%f%z')
    return datetime.datetime.now(tz=pytz.utc) - startTime

def appendStatus(fieldName, values):
    try:
        field = values[fieldName]
        # Do color coding on the status field
        if fieldName == 'status':
            if field == 'good':
                row = '<td style="background:green">' + field + '</td>'
            else:
                row = '<td style="background:red">' + field + '</td>'
        elif fieldName == 'timestamp':
            statusAge = timeSince(values[fieldName])
            if statusAge.seconds < 120:
                softTime = str(int(statusAge.seconds)) + ' seconds'
                color = 'green'
            elif statusAge.seconds < 600:
                softTime = 'more than ' + str(int((statusAge.seconds / 60) + 1)) + ' minutes'
                color = 'yellow'
            elif statusAge.seconds < 7200:
                softTime = 'more than ' + str(int((statusAge.seconds / 60) + 1)) + ' minutes'
                color = 'red'
            else:
                softTime = 'more than ' + str(int((statusAge.seconds / 3600) + 1)) + ' hours'
                color = 'red'
            row = '<td style="background:' + color + '">' + softTime + '</td>'
        elif fieldName == 'lastChanged':
            # Show the time since the status has last changed
            unchangedFor = timeSince(values[fieldName])
            # Pretty-formatting
            softTime = str(int(unchangedFor.seconds %60)) + 's'
            if unchangedFor.seconds > 60:
                unitTime = int(unchangedFor.seconds /60%60)
                timeUnit = 'm '
                softTime = str(unitTime).zfill(2) + timeUnit + softTime
                if unchangedFor.seconds > 3600:
                    unitTime = int(unchangedFor.seconds /3600%24)
                    timeUnit = 'h '
                    softTime = str(unitTime).zfill(2) + timeUnit + softTime
                    if unchangedFor.seconds > 86400:
                        unitTime = int(unchangedFor.seconds /86400)
                        timeUnit = 'd '
                        softTime = str(unitTime).zfill(2) + timeUnit + softTime
            row = '<td>' + softTime + '</td><!-- ' + values[fieldName] + ' -->'
        else:
            row =  '<td>' + values[fieldName] + '</td>'
    # To keep things aligned in case a field is empty
    except KeyError:
        row =  '<td></td>'
    return row

@route('/')
def index():
    statuses = []
    response =  '<head><meta http-equiv="refresh" content="60">\n'
    response += '<style>'
    response += 'table td{border: 1px solid black;}'
    response += '</style></head>'
    response += '<body>\n'
    response += '<table>\n'
    response += '<tr><td>Service</td><td>Type</td><td>Status</td>'
    response += '<td>Last Updated</td><td>Status Unchanged For</td><td>Notes</td></tr>\n'
    # For adding each status to the table
    # Crawl the statuses directory for all the things that I'm watching
    for listing in os.listdir(Kettles.statusFilesPath):
        a = Kettles.Status(listing)
        statuses.append(a)
    # Add the contents of those statuses to the response 
    for status in statuses:
        response += '<tr>'
        response += appendStatus('service', status.values)
        response += appendStatus('type', status.values)
        response += appendStatus('status', status.values)
        response += appendStatus('timestamp', status.values)
        response += appendStatus('lastChanged', status.values)
        response += appendStatus('notes', status.values)
        response += '</tr>\n'

    response += '</table>\n'
    response += '</body>'
    return response

run(host='0.0.0.0', port=8000)
