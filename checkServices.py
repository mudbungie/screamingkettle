#!/usr/bin/python3

## executes monitors found in the ./monitors/ directory, updating statuses
## in the ./statuses/ directory.

# name of the service to be monitored is the filename of the monitor file
# all other values are to be on their own lines, and delimited by an '='

import os
import monitorStatus
import sys

monitorFilesPath = sys.path[0] + os.sep + 'monitors/'

for serviceDefinitionFile in os.listdir(monitorFilesPath):
    # parse the config file into a dictionary
    directives = {'service': serviceDefinitionFile}
    with open(monitorFilesPath + serviceDefinitionFile, 'r') as serviceDefinition:
        for line in serviceDefinition.read().splitlines():
            # ignore commented lines
            if line.lstrip()[0] != '#':
                lineSplit = line.split('=', 1)
                directives[lineSplit[0]] = lineSplit[1]
        #test code
        #print(directives['service'] + ' ' + directives['serviceType'])
        # based on the service type, make an appropriate status object
        ## websites
        if directives['serviceType'] == 'website':
            # if there's a checkString, pass it
            try:
                status = monitorStatus.webStatus(directives['service'], 
                            directives['url'], directives['checkString'])
            # otherwise whatever
            except KeyError:
                status = monitorStatus.webStatus(directives['service'], 
                            directives['url'])
        ## minecraft servers
        elif directives['serviceType'] == 'minecraft':
            status = monitorStatus.minecraftStatus(directives['service'], 
                            directives['connectionString'])
        ## host pings
        elif directives['serviceType'] == 'ping':
            status = monitorStatus.pingStatus(directives['service'], 
                            directives['address'])
        elif directives['serviceType'] == 'portscan':
            status = monitorStatus.portStatus(directives['service'],
                            directives['address'], directives['port'])

        # write the status of the service to a file
        status.record(directives['service'])
