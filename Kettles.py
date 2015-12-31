import sys, os
import datetime, pytz
import requests
from mcstatus import MinecraftServer
import socket
import re

statusFilesPath = sys.path[0] + os.sep + 'statuses' + os.sep

# Parent class for statuses
# Not for implementation on its own; needs to get values from child classes
class Status:
    # For repopulating a status from a file
    # Gets shadowed by child classes
    def __init__(self, fileName):
        self.values = {'service': fileName.split('/')[-1]}
        with open(statusFilesPath + fileName) as statusFile:
                # Break on the first '=' sign to establish key-value pairs for a dictionary
                for line in statusFile.read().splitlines():
                    lineSplit = line.split('=', 1)
                    try:
                        self.values[lineSplit[0]] = lineSplit[1]
                    except IndexError:
                        pass
    
    def record(self, title):
        # Start out with a fresh timestamp
        timestamp = datetime.datetime.now(tz=pytz.utc).isoformat()
        self.values['timestamp'] = timestamp
        
        # Get the data from existing file
        statusFileName = statusFilesPath + title
        try:
            oldStatus = Status(title)
            # If the status is unchanged, we'll keep track of how long it's been that way
            if oldStatus.values['status'] == self.values['status']:
                self.values['lastChanged'] = oldStatus.values['lastChanged']
        except (FileNotFoundError, KeyError):
            # In case the status wasn't run before, or didn't include a lastChanged
            self.values['lastChanged'] = self.values['timestamp']

        # Writes the status to a file for use by the webserver
        with open(statusFilesPath + title, 'w') as statusFile:
            for key, value in self.values.items():
                statusFile.write(key + '=' + value + '\n')

class HttpStatus(Status):
    # Checks a site to see if it responds. Optionally verifies the contents of
    # The site to contain a string
    def getPage(self, url, checkString=False):
        try:
            self.page = requests.get(url)
            # If there was a string to check in the page
            if checkString:
                # then check for it
                if checkString in self.page.text:
                    self.values['status'] = 'good'
                else:
                    self.values['status'] = 'bad'
            else:
                self.values['status'] = 'good'
        except requests.exceptions.ConnectionError:
            self.values['status'] = 'bad'
        
    def __init__(self, service , url, checkString=False, notes=False):
        self.values = {'service': service, 'type': 'http'}
        if checkString:
            self.getPage(url, checkString)
        else:
            self.getPage(url, checkString)

class WebReport(HttpStatus):
    # Posts the output of an HTTP request to the notes field
    def __init__(self, service, url):
        self.values = {'service': service, 'type': 'webreport'}
        self.getPage(url)
        # Because Unicode
        self.values['notes'] = self.page.text.encode('ascii', 'ignore').decode()

class MinecraftStatus(Status):
    def __init__(self, service, connectionString):
        self.values = {'service': service, 'type': 'minecraft'}
        server = MinecraftServer.lookup(connectionString)
        try:
            status = server.status()
            self.values['status'] = 'good'
            self.values['notes'] = str(status.players.online) + ' players online'
        except ConnectionRefusedError:
            self.values['status'] = 'bad'
            self.values['notes'] = 'Connection refused'
        except socket.timeout:
            self.values['status'] = 'bad'
            self.values['notes'] = 'Connection timeout'
        except OSError:
            self.values['status'] = 'bad'
            self.values['notes'] = 'No response; likely booting'

class PingStatus(Status):
    # FULL WARNING: python3 can't intrinsically run pings without elevating
    # privileges and using a bunch of extra code. Just not in the system set.
    # So, I'm subscripting it to bash, and the local suid-enabled ping binary.
    def __init__(self, service, address):
        self.values = {'service': service, 'type': 'ping'}
        
        # this is silly, because it's your conf file, but I get really nervous
        # whenever I'm executing inputs directly into a shell, so sanitize!
        ## This matches dotted decimal IPv4 addresses
        if not re.match('([0-9]{1,3}\.){3}[0-9]', address):
            address = socket.gethostbyname(address)
        command = 'ping ' + address + ' -c 1 >/dev/null'

        # See if you can reach it
        ping = os.system(command)
        if ping == 0:
            self.values['status'] = 'good'
        else:
            self.values['status'] = 'bad'

class PortStatus(Status):
    def __init__(self, service, address, port):
        self.values = {'service': service, 'type': 'portscan'}
        a = socket.socket()
        a.settimeout(10)
        try:
            a.connect((address, int(port)))
            self.values['status'] = 'good'
        except ConnectionRefusedError:
            self.values['status'] = 'bad'
            self.values['notes'] = 'port closed'
        except OSError:
            self.values['status'] = 'bad'
            self.values['notes'] = 'port filtered'
