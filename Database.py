import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import requests
from mcstatus import MinecraftServer

engine = create_engine('sqlite:///screamingkettle.sqlite')
meta = MetaData()
Base = declarative_base(metadata=meta)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

class Service(Base):
    __tablename__ = 'services'
    serviceid = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    servicetype = Column(String(25), nullable=False)
    address = Column(String(25))
    port = Column(Integer)
    hasstring = Column(String(25)) # Verifies that content contains this value.
    tries = Column(Integer, default=3)
    report = Column(Boolean, default=True) # Whether or not it is displayed.

    @property
    def currentStatus(self):
        try:
            s = Session()
            return s.query(Status).filter(and_(Status.expired == None,
                Status.service == self.serviceid)).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return False
    def updateStatus(self, value):
        # Update the status if it has changed, do nothing otherwise.
        def newStatus(value, timestamp):
            s = Session()
            status = Status(good=value, service=self.serviceid, 
                observed=timestamp, lastchecked=timestamp)
            s.add(status)
            s.commit()

        print(self.name, 'value:', value)
        currentStatus = self.currentStatus
        timestamp = datetime.now()
        if currentStatus:
            currentStatus.lastchecked = timestamp
            if not currentStatus.good == value:
                currentStatus.expired = timestamp
                newStatus(value, timestamp)
            currentStatus.update()
        else:
            newStatus(value, timestamp)
    
    def html(self):
        timestamp = datetime.now()
        def softtime(seconds):
            softtime = ''
            if seconds > 86400:
                softtime += str(int(seconds/86400)) + 'd '
            if seconds > 3600:
                softtime += str(int(seconds%86400/3600)) + 'h '
            if seconds > 60:
                softtime += str(int(seconds%3600/60)) + 'm '
            softtime += str(seconds%60) + 's'
            return softtime
            
        def judgetime(seconds, dubious=120, bad=300):
            # Return a column with a class, depending the time.
            if seconds > dubious:
                if seconds > bad:
                    judgement = 'bad'
                else:
                    judgement = 'dubious'
            else:
                judgement = 'good'
            return judgement

        html =  '<tr>'
        html += '<td>' + self.name + '</td>'
        html += '<td>' + self.servicetype + '</td>'
        if self.currentStatus.good:
            html += '<td class="good">Good</td>'
        else:
            html += '<td class="bad">Bad</td>'
        age = timestamp - self.currentStatus.lastchecked
        html += '<td class="' + judgetime(age.seconds) + '">'
        html += softtime(age.seconds) + '</td>'
        age = timestamp - self.currentStatus.observed
        html += '<td>' + softtime(age.seconds) + '</td>'

        return html

    def check(self, tries=0):
        if tries != 0 or tries >= self.tries:
            # First thing's first, handle recursive retries.
            self.updateStatus(False)
            return False
        servicetype = self.servicetype
        if servicetype == 'port':
            s = socket.socket()
            s.settimeout(2)
            try:
                s.connect((self.address, self.port))
                self.updateStatus(True)
                print('check passed for', self.address, 'at', self.port)
            except (ConnectionRefusedError, OSError):
                # OSError is timeout, ConnectionRefusedError is a closed port.
                #FIXME Differentiate these errors when you add notes.
                print('check failed for', self.address, 'at', self.port)
                self.updateStatus(False)
                tries += 1
                self.check(tries=tries)
        elif servicetype == 'http' or servicetype == 'https':
            try:
                url = servicetype + '://' + self.address + str(self.port)
                p = requests.get(url)
                if self.hasstring:
                    if self.hasstring in p.text:
                        self.updateStatus(True)
                    else:
                        self.updateStatus(False)
                else:
                    self.updateStatus(True)
            # Requests has a lot of exceptions.
            except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout):
                    self.updateStatus(False)
        elif servicetype == 'minecraft':
            server = MinecraftServer.lookup(self.address + ':' + \
                str(self.port))
            try:
                status = server.status()
                self.updateStatus(True)
            except (ConnectionRefusedError, socket.timeout, OSError):
                self.updateStatus(False)
            

class Status(Base):
    __tablename__ = 'statuses'
    statusid = Column(Integer, primary_key=True)
    good = Column(Boolean, nullable=False)
    service = Column(ForeignKey('services.serviceid'), nullable=False)
    lastchecked = Column(DateTime, nullable=False)
    observed = Column(DateTime, nullable=False)
    expired = Column(DateTime)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
# Class for a service, as defined in the database.
# Has methods to check itself, find if it has wrecked itself.

from Database import Service, Status, Session
import socket

