#!/usr/bin/python3

## Executes monitors found in the ./monitors/ directory, updating statuses
## in the ./statuses/ directory.

# Name of the service to be monitored is the filename of the monitor file
# all other values are to be on their own lines, and delimited by an '='

import os
import Kettles
import sys
from multiprocessing import Process

monitorFilesPath = sys.path[0] + os.sep + 'monitors' + os.sep

def getServiceDefinitions(path):
    serviceDefinitions = []
    for serviceDefinitionFile in os.listdir(monitorFilesPath):
        # Parse the config file into a dictionary
        directives = {'service': serviceDefinitionFile}
        with open(monitorFilesPath + serviceDefinitionFile, 'r') as serviceDefinition:
            for line in serviceDefinition.read().splitlines():
                # Ignores commented lines
                if line.lstrip()[0] != '#':
                    lineSplit = line.split('=', 1)
                    directives[lineSplit[0]] = lineSplit[1]
        serviceDefinitions.append(directives)
    return serviceDefinitions

def spawnChecks(path):
    # For each status that we're checking, fork
    newPid = 0
    serviceDefinitions = getServiceDefinitions(path)
    for serviceDefinition in serviceDefinitions:
        if newPid == 0:
            newPid = os.fork()
        if newPid != 0:
            checkStatus(serviceDefinition)

def checkStatus(directives):
    ## http
    if directives['serviceType'] == 'http':
        # If there's a checkString, pass it
        try:
            status = Kettles.HttpStatus(directives['service'], 
                        directives['url'], directives['checkString'])
        # Otherwise whatever
        except KeyError:
            status = Kettles.HttpStatus(directives['service'], 
                        directives['url'])
    ## takes the output of a webserver and posts it
    if directives['serviceType'] == 'webreport':
        status = Kettles.WebReport(directives['service'],
                        directives['url'])
    ## minecraft servers
    elif directives['serviceType'] == 'minecraft':
        status = Kettles.MinecraftStatus(directives['service'], 
                        directives['connectionString'])
    ## ping
    elif directives['serviceType'] == 'ping':
        status = Kettles.PingStatus(directives['service'], 
                        directives['address'])
    ## check if a port is open
    elif directives['serviceType'] == 'portscan':
        status = Kettles.PortStatus(directives['service'],
                        directives['address'], directives['port'])

    # Write the status of the service to a file
    status.record(directives['service'])

spawnChecks(monitorFilesPath)
