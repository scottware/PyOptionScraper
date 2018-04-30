import datetime
import time
import urllib.request
import urllib.parse
import json.decoder
from multiprocessing.dummy import Pool as ThreadPool

from requests import HTTPError

from Option import Option
from Option import OptionType

from Stock import *
from pprint import pprint
import datetime


class TDAStockOptionFetcher:
    _baseUrl = "https://api.tdameritrade.com/v1/marketdata/chains?"

    def __init__(self, config):
        self._config = config

    def fetchdata(self, stock):
        self.stock=stock
        urlParams = {'apikey': self._config['tda_api_key'],
                  'symbol': stock.getSymbol(),
                  'contractType': "PUT", 'range': 'OTM', 'OptionType': 'S'}
        url = self._baseUrl + urllib.parse.urlencode(urlParams)

        with urllib.request.urlopen(url) as response:
            html = response.read()
        d = json.loads(html)

        self.stock.setUnderlyingPrice(d['underlyingPrice'])

        putExpDateMap = d['putExpDateMap']
        putExpDates = putExpDateMap.keys()
        today = datetime.datetime.utcnow()

        optionSet = []
        for expiryDays in putExpDates:
            date, days = expiryDays.split(':')
            pattern = '%Y-%m-%d'
            epoch = int(time.mktime(time.strptime(date, pattern)))
            # todo this is in localtime. Probably is supposed to be 4pm est
            # todo this is just a hack...
            tmp = epoch // 86400
            epoch = tmp * 86400

            thisDateMap = putExpDateMap[expiryDays]
            for strike in thisDateMap.keys():
                bid = thisDateMap[strike][0]['bid']
                ask = thisDateMap[strike][0]['ask']
                last = thisDateMap[strike][0]['last']
                option = Option(self.stock, OptionType.PUT, float(strike), last, ask, bid,
                                today)
                option.setExpirationDate(epoch)
                option.setApr()
                optionSet.append(option)

        return optionSet
