import itertools

from Stock import *
from YahooStockOptionFetcher import *
from TDAStockOptionFetcher import *
import configparser
from GoogleSheetWriter import *
from datetime import datetime

configuration = configparser.ConfigParser()
configuration.read('example.ini')

config = {'stockList': configuration['DEFAULT'].get('symbol').split(','),
          'option_type': configuration['DEFAULT'].get('option_type', 'put').upper(),
          'filter_apr_low': configuration['DEFAULT'].getfloat('filter_apr_low', 0.0),
          'filter_apr_high': configuration['DEFAULT'].getfloat('filter_apr_high', 100.0),
          'filter_strike_high': configuration['DEFAULT'].getfloat('filter_strike_high'),
          }

source = configuration['DEFAULT'].get('source').upper()

def sofFactory():
    if source == 'YHOO':
        return YahooStockOptionFetcher(config)
    if source == 'TDA':
        configTDA = configparser.ConfigParser()
        configTDA.read('configTDA.ini')
        config['tda_api_key'] = configTDA['TDA'].get('tda_api_key')
        return TDAStockOptionFetcher(config)


def go(stockSymbol, goog=False):
    print(stockSymbol + "=================================")
    stock = Stock(stockSymbol)

    sof=sofFactory();

    options = stock.loadData(sof)
    options.sort(key=lambda x: x.getApr(), reverse=True)
    outputList = filter(lambda x: x.getType() == OptionType[config['option_type']], options)
    outputList = filter(lambda x: x.getApr() <= config['filter_apr_high'], outputList)
    outputList = filter(lambda x: x.getApr() >= config['filter_apr_low'], outputList)
    # outputList = filter(lambda x: x.getStrikePrice() <= config['filter_strike_high'], outputList)
    outputList = filter(lambda x: x.getStrikePrice() <= stock.getUnderlyingPrice(), outputList)

    listOptions = list(outputList)
    for option in listOptions:
        print(option)

    if (goog):
        GSW = GoogleSheetWriter()
        GSW.write(stock, listOptions)


startTime = datetime.now()

x = True
goog = True

if (x):
    stockList = config['stockList']
    pool = ThreadPool(4)
    optionsLists = pool.starmap(go, zip(stockList, itertools.repeat(goog)))
    pool.close()
    pool.join()

time = datetime.now() - startTime
print(time)
