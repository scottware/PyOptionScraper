import datetime
import time
import urllib.request
import urllib.error
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
        #pprint(self._config)
        self.stock = stock
        urlParams = {'apikey': self._config['tda_api_key'],
                     'symbol': stock.getSymbol(),
                     'contractType': "PUT", 'range': 'OTM', 'OptionType': 'S'}
        url = self._baseUrl + urllib.parse.urlencode(urlParams)

        args = urllib.parse.urlencode(urlParams).encode("utf-8")
        headers = {}
        useAccessToken = True
        if useAccessToken == True:
            headers = {"Authorization": "Bearer {0}".format(self._config['access_token'])}

        request = urllib.request.Request(url, headers=headers, method='GET')

        #pprint(request.get_full_url())
        #pprint(request.headers)
        #pprint(request.data)
        #pprint(request.get_method())

        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            if e.code==401:
                print("v" * 20)
                print("Error occurred fetching {0}".format(request.get_full_url()))
                print(e)
                print("off to fetch new tokens")
                print("^" * 20)
                self.refreshToken()
        else:
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

    def oauth(self, step):
        if step == 1:
            import webbrowser
            authorize_url = "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=http%3a%2f%2flocalhost%3a8080&client_id=sware%40AMER.OAUTHAP"
            webbrowser.open(authorize_url, new=1, autoraise=True)
            # copy resulting string from after code=. url decode. let that become self._code
            print("type what is after 'code=' in the URI:")
            code = urllib.parse.unquote(input())

            self._code = code
            step = 2
        if step == 2:
            step2url = "https://api.tdameritrade.com/v1/oauth2/token?"
            step2args = {'grant_type': 'authorization_code', 'refresh_token': '', 'access_type': 'offline',
                         'code': self._code, 'client_id': self._config['tda_api_key'], 'redirect_uri': 'http://localhost:8080'}
            args = urllib.parse.urlencode(step2args).encode("utf-8")

            headers = {"Content-Type": 'application/x-www-form-urlencoded'}

            request = urllib.request.Request(step2url, data=args, headers=headers, method='POST')

            pprint(request.get_full_url())
            pprint(request.headers)

            try:
                response = urllib.request.urlopen(request)
            except urllib.error.HTTPError as e:
                print("v" * 20)
                print("Error occurred fetching {0}".format(request.get_full_url()))
                print(e)
                print("^" * 20)
            else:
                html = response.read()
                d = json.loads(html)
                pprint(d)

                # TODO: abstract config saving out. This is duplicate code from self.refreshToken()
                # configTDA = configparser.ConfigParser()
                configTDA.read('configTDA.ini')
                if not 'OAUTH' in configTDA.sections():
                    configTDA.add_section('OAUTH')
                configTDA.set('OAUTH', 'refresh_token', d['refresh_token'])
                configTDA.set('OAUTH', 'access_token', d['access_token'])
                with open('configTDA.ini', 'w') as configfile:
                    configTDA.write(configfile)

    def refreshToken(self):
        refreshUrl = "https://api.tdameritrade.com/v1/oauth2/token"
        refreshArgs = {'grant_type': 'refresh_token', 'refresh_token': self._config['refresh_token'], 'access_type': '',
                       'code': '', 'client_id': self._config['tda_api_key'], 'redirect_uri': ''}

        args = urllib.parse.urlencode(refreshArgs).encode("utf-8")

        headers = {"Content-Type": 'application/x-www-form-urlencoded'}
        request = urllib.request.Request(refreshUrl, data=args, headers=headers, method='POST')

        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            print("v"*20)
            print("Error occurred fetching {0}".format(request.get_full_url()))
            print(request.data)
            print(e)
            print("^"*20)
            self.oauth(1)
        else:
            html = response.read()
            d = json.loads(html)
            new_access_token = d['access_token']
            print("new access token: {0}".format(new_access_token))

            # TODO: abstract config saving out. This is duplicate code from self.oauth()
            configTDA = configparser.ConfigParser()
            configTDA.read('configTDA.ini')
            if not 'OAUTH' in configTDA.sections():
                configTDA.add_section('OAUTH')
            configTDA.set('OAUTH', 'access_token', d['access_token'])
            with open('configTDA.ini', 'w') as configfile:
                configTDA.write(configfile)



# tda = TDAStockOptionFetcher(1)
# tda.oauth(1)
# tda.fetchdata(Stock('AMZN'))


import configparser

configuration = configparser.ConfigParser()
configuration.read('example.ini')

config = {'stockList': configuration['DEFAULT'].get('symbol').split(','),
          'option_type': configuration['DEFAULT'].get('option_type', 'put').upper(),
          'filter_apr_low': configuration['DEFAULT'].getfloat('filter_apr_low', 0.0),
          'filter_apr_high': configuration['DEFAULT'].getfloat('filter_apr_high', 100.0),
          'filter_strike_high': configuration['DEFAULT'].getfloat('filter_strike_high'),
          }

source = configuration['DEFAULT'].get('source').upper()

configTDA = configparser.ConfigParser()
configTDA.read('configTDA.ini')
config['tda_api_key'] = configTDA['TDA'].get('tda_api_key')
config['access_token'] = configTDA['OAUTH'].get('access_token')
config['refresh_token'] = configTDA['OAUTH'].get('refresh_token')


tda = TDAStockOptionFetcher(config)
# tda.refreshToken()
#tda.oauth(1)
tda.fetchdata(Stock("AMZN"))
