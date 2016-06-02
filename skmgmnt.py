#!/usr/bin/env python3

# Command-line database frontend for ScreamingKettle.

from Database import *
from datetime import datetime

def addStatus(**kw):
    s = Session()
    service = Service(  name=kw['name'], 
                        servicetype=kw['servicetype'],
                        address=kw['address'],
                        port=kw['port'],
                        )
    s.add(service)
    s.flush()
    # Add a bad status to get us started.
    #status = Status(good=False, service=service.serviceid, observed=datetime.now())
    #s.add(status)

    s.commit()
    service.check()

if __name__ == '__main__':
    new = input('Make a new service?[yN]')
    if new.lower() == 'y':
        name = input('Service name:')
        servicetype = input('Service type:')
        address = input('Address:')
        port = input('Port:')
        hasstring = input('Check for a string?: (Blank for none)')
        if len(hasstring) == 0:
            hasstring = False
        addStatus(name=name, servicetype=servicetype, address=address, 
            port=port)
    else:
        s = Session()
        for service in s.query(Service).all():
            print('Checking service:', service.name)
            service.check()
