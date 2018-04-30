import datetime
import urllib.request
import json.decoder
from multiprocessing.dummy import Pool as ThreadPool

from Option import Option
from Option import OptionType


class YahooStockOptionFetcher:
    equityUrl = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
    optionUrl = "https://query1.finance.yahoo.com/v7/finance/options/"
    optionDateBaseUrl = "https://query1.finance.yahoo.com/v7/finance/options/"

    def __init__(self, config):
        self._config = config

    def fetchdata(self, stock):
        self.stock=stock
        return self.fetchdataParallel(stock)

    def fetchdataParallel(self, stock):
        price = self.fetchSharePrice()
        stock.setUnderlyingPrice(price)
        optionDates = self.fetchOptionDates()

        pool = ThreadPool(5)

        optionDateUrls = [self.optionDateBaseUrl + stock.getSymbol() + "?date=" + str(date) for date in optionDates]

        optionsLists = pool.starmap(self.fetchExpirationDate, zip(optionDateUrls, optionDates))
        options = [item for sublist in optionsLists for item in sublist]

        pool.close()
        pool.join()

        return options

    def parse(self, html):
        print(html)
        d = json.loads(html)

    #        print(json.dumps(d, indent=4, sort_keys=True))

    def fetchExpirationDate(self, dateUrl, date):
        # date as epoch time
        today = datetime.datetime.utcnow()
        optionSet = []
        print("Fetching {0}".format(dateUrl))
        with urllib.request.urlopen(dateUrl) as response:
            html = response.read()
        d = json.loads(html)
        calls = d['optionChain']['result'][0]['options'][0]['calls']
        puts = d['optionChain']['result'][0]['options'][0]['puts']
        for put in puts:
            option = Option(self.stock, OptionType.PUT, put['strike'], put['lastPrice'], put['ask'], put['bid'], today)
            option.setExpirationDate(date)
            option.setApr()
            optionSet.append(option)
        for call in calls:
            option = Option(self.stock, OptionType.CALL, call['strike'], call['lastPrice'], call['ask'], call['bid'],
                            today)
            option.setExpirationDate(date)
            option.setApr()
            optionSet.append(option)
        return optionSet

    def fetchSharePrice(self):
        with urllib.request.urlopen(self.equityUrl + self.stock.getSymbol()) as response:
            html = response.read()
        d = json.loads(html)
        return d['quoteResponse']['result'][0]['regularMarketPrice']

    def fetchOptionDates(self):
        with urllib.request.urlopen(self.optionUrl + self.stock.getSymbol()) as response:
            html = response.read()
        d = json.loads(html)
        return d['optionChain']['result'][0]['expirationDates']
