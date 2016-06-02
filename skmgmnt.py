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
    status = Status(good=False, service=service.serviceid, observed=datetime.now())
    s.add(status)
    s.commit()

if __name__ == '__main__':
    addStatus(name='test', servicetype='port', address='127.0.0.1', port=22)
