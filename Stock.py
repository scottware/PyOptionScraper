from YahooStockOptionFetcher import *
#from TDAStockOptionFetcher import *


class Stock:
    options = []

    def __init__(self, symbol):
        self.symbol = symbol

    def setSymbol(self, symbol):
        self.symbol = symbol

    def getSymbol(self):
        return self.symbol

    def setUnderlyingPrice(self, price):
        self.underlying_price = price
        print(f"Underlying price set to: {price}")

    def getUnderlyingPrice(self):
        return self.underlying_price

    def loadData(self, stockOptionFetcher):
        if (len(self.options)==0):
            sof = YahooStockOptionFetcher(self)
            #sof = TDAStockOptionFetcher(self)
            #list = sof.fetchdata(self)
            list = sof.fetchdataParallel(self)
            #sof.parse(list)
            #sof.fetchSharePrice()
            return list

    def __str__(self):
        return "{0} {1: 7.2f}".format(self.getSymbol(),self.getUnderlyingPrice())