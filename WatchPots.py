#!/usr/bin/python3

## Executes monitors found in the ./monitors/ directory, updating statuses
## in the ./statuses/ directory.

# Name of the service to be monitored is the filename of the monitor file
# all other values are to be on their own lines, and delimited by an '='

import os
import Kettles
import sys
from multiprocessing import Process
from configobj import ConfigObj

# Load a config file
whereAmI = os.path.dirname(os.path.abspath(__file__)) + '/'
config = ConfigObj(whereAmI + 'screamingkettle.conf')

def spawnChecks():
    # For each status that we're checking, fork
    newPid = 0
    serviceDefinitions = []
    for service, values in config.items():
        values['service'] = service
        serviceDefinitions.append(values)

    for serviceDefinition in serviceDefinitions:
        if newPid == 0:
            newPid = os.fork()
            if newPid != 0:
                checkStatus(serviceDefinition)

def checkStatus(directives):
    ## http
    if directives['type'] == 'http':
        # If there's a checkString, pass it
        try:
            status = Kettles.HttpStatus(directives['service'], 
                        directives['url'], directives['checkString'])
        # Otherwise whatever
        except KeyError:
            status = Kettles.HttpStatus(directives['service'], 
                        directives['url'])
    ## takes the output of a webserver and posts it
    if directives['type'] == 'webreport':
        status = Kettles.WebReport(directives['service'],
                        directives['url'])
    ## minecraft servers
    elif directives['type'] == 'minecraft':
        status = Kettles.MinecraftStatus(directives['service'], 
                        directives['connectionString'])
    ## ping
    elif directives['type'] == 'ping':
        status = Kettles.PingStatus(directives['service'], 
                        directives['address'])
    ## check if a port is open
    elif directives['type'] == 'portscan':
        status = Kettles.PortStatus(directives['service'],
                        directives['address'], directives['port'])

    # Write the status of the service to a file
    status.record(directives['service'])

if __name__ == '__main__':
    spawnChecks()
