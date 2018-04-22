from Stock import *
from YahooStockOptionFetcher import *
import configparser
from GoogleSheetWriter import *


config = configparser.ConfigParser()
config.read('example.ini')

config = {'stockList': config['DEFAULT'].get('symbol').split(','),
          'option_type': config['DEFAULT'].get('option_type', 'put').upper(),
          'filter_apr_low': config['DEFAULT'].getfloat('filter_apr_low', 0.0),
          'filter_apr_high': config['DEFAULT'].getfloat('filter_apr_high', 100.0),
          'filter_strike_high': config['DEFAULT'].getfloat('filter_strike_high')
          }



x = True
goog= True

if (x):
    for stock in config['stockList']:
        print(stock+"=================================")
        stock = Stock(stock)
        options = stock.loadData(YahooStockOptionFetcher(stock))
        options.sort(key=lambda x: x.getApr(), reverse=True)
        outputList = filter(lambda x: x.getType() == OptionType[config['option_type']], options)
        outputList = filter(lambda x: x.getApr() <= config['filter_apr_high'], outputList)
        outputList = filter(lambda x: x.getApr() >= config['filter_apr_low'], outputList)
        #outputList = filter(lambda x: x.getStrikePrice() <= config['filter_strike_high'], outputList)
        outputList = filter(lambda x: x.getStrikePrice() <= stock.getUnderlyingPrice(), outputList)

        listOptions = list(outputList)
        for option in listOptions:
            print(option)

        if(goog):
            GSW=GoogleSheetWriter()
            GSW.write(stock,listOptions)