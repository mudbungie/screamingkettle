import sys, os
import datetime, pytz
import urllib.request
from mcstatus import MinecraftServer
import socket
import re

statusFilesPath = sys.path[0] + os.sep + 'statuses/'

# parent class for statuses
# not for implementation on its own; needs to get values from child classes
class status:
    def record(self, title):
        # writes the status to a file for use by the webserver
        timestamp = datetime.datetime.now(tz=pytz.utc).isoformat()
        with open(statusFilesPath + title, 'w') as statusFile:
            # start out with a fresh timestamp
            self.values['timestamp'] = timestamp
            for key, value in self.values.items():
                statusFile.write(key + '=' + value + '\n')

class recordedStatus(status):
    # for repopulating a status from a file
    def __init__(self, fileName):
        self.values = {'service': fileName.split('/')[-1]}
        with open(statusFilesPath + fileName) as statusFile:
                # break on the first '=' sign to establish key-value pairs for a dictionary
                for line in statusFile.read().splitlines():
                    lineSplit = line.split('=', 1)
                    self.values[lineSplit[0]] = lineSplit[1]

class webStatus(status):
    # checks a site to see if it responds. Optionally verifies the contents of
    # the site to contain a string
    def __init__(self, service , url, checkString=False):
        self.values = {'service': service, 'type': 'http'}
        try:
            page = urllib.request.urlretrieve(url)
            self.values['status'] = 'good'
        except urllib.error.URLError:
            self.values['status'] = 'bad'
        self.record(service)

class minecraftStatus(status):
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
        self.record(service)

class pingStatus(status):
    # FULL WARNING: python3 can't intrinsically run pings without elevating
    # privileges and using a bunch of extra code. Just not in the system set.
    # So, I'm subscripting it to bash, and the local suid-enabled ping binary.
    def __init__(self, service, address):
        self.values = {'service': service, 'type': 'ping'}
        
        # this is silly, because it's your conf file, but I get really nervous
        # whenever I'm executing inputs directly into a shell, so sanitize!
        ## this matches dotted decimal IPv4 addresses
        if not re.match('([0-9]{1,3}\.){3}[0-9]', address):
            address = socket.gethostbyname(address)
        command = 'ping ' + address + ' -c 1 >/dev/null'

        # see if you can reach it
        ping = os.system(command)
        if ping == 0:
            self.values['status'] = 'good'
        else:
            self.values['status'] = 'bad'
        self.record(service)

class portStatus(status):
    def __init__(self, service, address, port):
        self.values = {'service': service, 'type': 'portscan'}
        a = socket.socket()
        a.settimeout(10)
        try:
            a.connect((address, int(port)))
            self.values['status'] = 'good'
        except ConnectionRefusedError:
            self.values['status'] = 'bad'
        self.record(service)
