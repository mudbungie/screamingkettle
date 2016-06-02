class TimeDifference:
    def __init__(self, dt):
        startTime = dateParse(timeString)
        difference = datetime.datetime.now(tz=pytz.utc) - startTime
        # For some obscene reason, there isn't a builtin return of all seconds
        self.totalSeconds = int(difference.seconds) + difference.days * 86400
        self.seconds = int(difference.seconds % 60)
        self.minutes = int(difference.seconds / 60 % 60)
        self.hours   = int(difference.seconds / 3600 % 24)
        self.days    = int(difference.days)

        self.softTime = ''
        def appendToSoftTime(unitTime, timeUnit):
            # Trims leading empty time units
            if unitTime != 0 or len(self.softTime) > 0:
                self.softTime = self.softTime + str(unitTime).zfill(2) + timeUnit
        appendToSoftTime(self.days, 'd ')
        appendToSoftTime(self.hours, 'h ')
        appendToSoftTime(self.minutes, 'm ')
        appendToSoftTime(self.seconds, 's')
