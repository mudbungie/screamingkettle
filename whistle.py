#!/usr/bin/python3

# the main page; shows a list of red/green icons, depending on whether the 
# service passed muster last time it was checked. If there were notes left
# by the monitor daemons, they will be printed following the status icons

from bottle import route, run, template
import datetime, pytz
import os.path
import kettles

def timeSince(timeString):
    startTime = datetime.datetime.strptime(timeString.replace(':',''),
                        '%Y-%m-%dT%H%M%S.%f%z')
    return datetime.datetime.now(tz=pytz.utc) - startTime

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
    response += '<td>Last Updated</td><td>Unchanged For</td><td>Notes</td></tr>\n'
    # for adding each status to the table
    def appendStatus(fieldName, values):
        try:
            field = values[fieldName]
            # do color coding on the status field
            if fieldName == 'status':
                if field == 'good':
                    row = '<td style="background:green">' + field + '</td>'
                else:
                    row = '<td style="background:red">' + field + '</td>'
            elif fieldName == 'timestamp':
                # really ugly conversion from string to datetime
                #lastUpdated = datetime.datetime.strptime(values[fieldName].replace(':',''),
                #                                        '%Y-%m-%dT%H%M%S.%f%z')
                #statusAge = datetime.datetime.now(tz=pytz.utc) - lastUpdated
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
                # show the time since the status has last changed
                unchangedFor = timeSince(values[fieldName])
                # pretty-formatting
                softTime = str(int(unchangedFor.seconds %60)) + ' seconds'
                if unchangedFor.seconds > 60:
                    unitTime = int(unchangedFor.seconds /60%60)
                    if unitTime == 1:
                        timeUnit = ' minute '
                    else:
                        timeUnit = ' minutes '
                    softTime = str(unitTime) + timeUnit + softTime
                    if unchangedFor.seconds > 3600:
                        unitTime = int(unchangedFor.seconds /3600%24)
                        if unitTime == 1:
                            timeUnit = ' hour '
                        else:
                            timeUnit = ' hours '
                        softTime = str(unitTime) + timeUnit + softTime
                        if unchangedFor.seconds > 86400:
                            unitTime = int(unchangedFor.seconds /86400)
                            if unitTime == 1:
                                timeUnit = ' day '
                            else:
                                timeUnit = ' days '
                            softTime = str(unitTime) + ' days ' + softTime
                row = '<td>' + softTime + '</td><!-- ' + values[fieldName] + ' -->'
            else:
                row =  '<td>' + values[fieldName] + '</td>'
        # to keep things aligned in case a field is empty
        except KeyError:
            row =  '<td></td>'
        return row
    # crawl the statuses directory for all the things that I'm watching
    for listing in os.listdir(kettles.statusFilesPath):
        a = kettles.status(listing)
        statuses.append(a)
    # add the contents of those statuses to the response 
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
