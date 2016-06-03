#!/usr/bin/env python3

from Database import *
from datetime import datetime
from time import sleep

def checkServices():
    s = Session()
    services = s.query(Service).all()
    # Filter services by those with a last updated larger than their interval.
    for service in services:
        timestamp = datetime.now()
        age = timestamp - service.currentStatus.lastchecked
        if age.seconds > service.interval:
            service.check()

if __name__ == '__main__':
    while true:
        checkServices()
        sleep(1)
        
            
