import enum
import math

import pytz
import datetime


class OptionType(enum.Enum):
    PUT = 'PUT'  # 1
    CALL = 'CALL'  # 0
    ANY = 'ANY'  # -1

    def __str__(self):
        return self.name


class Option:
    def __init__(self, stock, type, strike, price, ask, bid, today):
        self._stock = stock
        self._type = type
        self._strike = strike
        self._price = price
        self._ask = ask
        self._bid = bid
        self._today = today

    def setExpirationDate(self, expirationDate):
        if expirationDate % 86400 != 0:
            return

        date = datetime.datetime.fromtimestamp(expirationDate)
        est = pytz.timezone('America/New_York')
        gmt = pytz.timezone('GMT')
        diff = gmt.utcoffset(date) - est.utcoffset(date)
        self._expirationDate = datetime.datetime.fromtimestamp(expirationDate + diff.seconds + 16 * 60 * 60)

    def getExpirationDate(self):
        return self._expirationDate.strftime("%m/%d/%Y")

    def setStrikePrice(self, price):
        self._strike = price

    def getStrikePrice(self):
        return self._strike

    def setPrice(self, price):
        self._price = price

    def getPrice(self):
        return self._price

    def getBidPrice(self):
        return self._bid

    def getAskPrice(self):
        return self._ask

    def getType(self):
        return self._type

    def isType(self, optionType):
        if (self.getType() == optionType or optionType == OptionType.ANY):
            return True
        else:
            return False

    def setApr(self):
        diff = self._expirationDate - datetime.datetime.utcnow()
        years = (diff.days + diff.seconds / 86400) / 365

        if self.getBidPrice() >= self.getStrikePrice():
            self._apr = 0
        else:
            self._apr = 100 * math.log((self.getStrikePrice()) / (self.getStrikePrice() - self.getBidPrice())) / years

        # print("{0:.2f} {1:.2f} {2:.2f}".format(self._apr,self.getStrikePrice(),self.getBidPrice()))

    def getApr(self):
        return self._apr

    def __str__(self):
        return "{0} {1}".format(str(self.getType()), self.getExpirationDate()) + \
               "   ${0:7.2f} ".format(self.getStrikePrice()) + \
               " ${0:7.2f} {1: 7.2f} {2: 7.2f}".format(self.getPrice(), self.getAskPrice(), self.getBidPrice()) + \
               " {0: >6.2f}%".format(self.getApr())

    def toList(self):
        s = str(self)
        l =s.split()

    __repr__ = __str__


test=False

if test==True:
    import calendar
    d=datetime.datetime(2018,5,18,0,0,0,0,tzinfo=pytz.timezone('GMT'))
    timestamp = calendar.timegm(d.timetuple())

    option = Option('AMZN', 'PUT', 1350,1430.79, 19.5, 16.85, datetime.datetime.utcnow())
    option.setExpirationDate(timestamp)
    option.setApr()
    print(option)
    datetime.datetime.utcnow()

    option2 = Option('AMZN', 'PUT', 1300,1430.79, 20.1, 17.40, datetime.datetime.utcnow())
    option2.setExpirationDate(timestamp)
    option2.setApr()
    print(option2)

    l=option.__str__().split()
    print(l)