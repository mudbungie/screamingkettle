import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

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
    hasstring = Column(String(25)) # Verifies that content contains this value.
    port = Column(Integer)
    report = Column(Boolean, default=True) # Whether or not it is displayed.

    @property
    def currentStatus(self):
        return Session.query(Status).filter(and_(Status.expired == None,
            Status.service == self.serviceid))
    def updateStatus(self, value):
        # Update the status if it has changed, do nothing otherwise.
        if self.currentStatus.good != value:
            timestamp = datetime.now()
            self.currentStatus.expired = timestamp
            s = Session()
            s.add(Status(good=value, service=self.serviceid, 
                observed=timestamp))
            s.commit()

    def check(self):
        s = socket.socket()
        s.settimeout(2)
        try:
            s.connect((self.address, self.port))
            self.updateStatus(True)
        except (ConnectionRefusedError, OSError):
            # OSError is timeout, ConnectionRefusedError is a closed port.
            #FIXME Differentiate these errors when you add notes.
            self.updateStatus(False)

class Status(Base):
    __tablename__ = 'statuses'
    statusid = Column(Integer, primary_key=True)
    good = Column(Boolean, nullable=False)
    service = Column(ForeignKey('services.serviceid'), nullable=False)
    observed = Column(DateTime, nullable=False)
    expired = Column(DateTime)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
# Class for a service, as defined in the database.
# Has methods to check itself, find if it has wrecked itself.

from Database import Service, Status, Session
import socket

