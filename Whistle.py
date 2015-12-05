#!/usr/bin/python3

# The main page; shows a list of red/green icons, depending on whether the 
# service passed muster last time it was checked. If there were notes left
# by the monitor daemons, they will be printed following the status icons.

from bottle import route, run, template
import datetime, pytz
import os.path
import Kettles

class TimeDifference:
    def __init__(self, timeString):
        startTime = datetime.datetime.strptime(timeString.replace(':',''),
                            '%Y-%m-%dT%H%M%S.%f%z')
        difference = datetime.datetime.now(tz=pytz.utc) - startTime
        self.seconds = int(difference.seconds % 60)
        self.minutes = int(difference.seconds / 60 % 60)
        self.hours   = int(difference.seconds / 3600 % 24)
        self.days    = int(difference.seconds / 86400)
        
        self.softTime = ''
        def appendToSoftTime(unitTime, timeUnit):
            # trims leading units with zeros
            if unitTime != 0 or len(self.softTime) > 0:
                self.softTime = self.softTime + str(unitTime).zfill(2) + timeUnit
        appendToSoftTime(self.days, 'd ')
        appendToSoftTime(self.hours, 'h ')
        appendToSoftTime(self.minutes, 'm ')
        appendToSoftTime(self.seconds, 's')

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
            statusAge = TimeDifference(values[fieldName])
            if statusAge.minutes < 2:
                color = 'green'
            elif statusAge.minutes < 10:
                color = 'yellow'
            else:
                color = 'red'
            row = '<td style="background:' + color + '">' + statusAge.softTime + '</td>'
        
        elif fieldName == 'lastChanged':
            lastChanged = TimeDifference(values[fieldName])
            row = '<td>' + lastChanged.softTime + '</td><!-- ' + values[fieldName] + ' -->'

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