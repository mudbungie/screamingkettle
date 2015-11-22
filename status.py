import datetime, pytz

# parent class for statuses
# not for implementation on its own; needs to get values from child classes
class status:
    def __init__():
        self.values = {}

    def record(title):
        # writes the status to a file for use by the webserver
        timestamp = datetime.datetime.now(tz=pytz.utc).strftime()
        with open('statuses/' + title, 'w') as statusFile:
            # start out with a fresh timestamp
            self.values['timestamp'] = timestamp
            for key, value in self.values.items():
                statusFile.write(key + '=' + value)

class recordedStatus(status):
    # for repopulating a status from a file
    def __init__(title):
    self.values = {}
    with open('statuses/' + title, 'r') as statusFile:
            # break on the first '=' sign to establish key-value pairs for a dictionary
            for line in statusFile.read():
                lineSplit = line.split('=', 1)
                values[lineSplit[0]] = lineSplit[1])
