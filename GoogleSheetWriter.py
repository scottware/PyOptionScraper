from __future__ import print_function

from pprint import pprint
import gspread
import gspread.utils

from oauth2client import file, client, tools


class GoogleSheetWriter:
    # Setup the Sheets API
    _SCOPES = ['https://spreadsheets.google.com/feeds',
               'https://www.googleapis.com/auth/drive']

    def __init__(self):
        self._doc = self.connect()

    def connect(self):
        store = file.Storage('credentials.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', self._SCOPES)
            creds = tools.run_flow(flow, store)
        connection = gspread.authorize(creds)

        # Call the Sheets API
        SPREADSHEET_ID = '10nVsQJdyIA2jFlpTUWY-dlXKPAYQbbGmxqU241YwUGU'

        return connection.open_by_key(SPREADSHEET_ID)

    def write(self, stock, options):
        print(stock)

        sheets = self._doc.worksheets()
        name = stock.getSymbol()

        q = [x for x in sheets if x._properties['title'] == name]
        if q:
            self._doc.del_worksheet(q[0])
        sheet = self._doc.add_worksheet(name, 1000, 26)

        rowcount=len(options)
        colcount=len(options[0].__repr__().split())

        textSubList = [i.__repr__().split() for i in options]
        textList = [item for sublist in textSubList for item in sublist]
        textIter = iter(textList)

        endCell =gspread.utils.rowcol_to_a1(rowcount,colcount)
        cell_list = sheet.range("A1:{0}".format(endCell))

        for cell in cell_list:
            try:
                cell.value="{0}".format(textIter.__next__())
            except StopIteration:
                pprint(cell)
                print(cell.value)


        sheet.update_cells(cell_list)

        sheet.update_cell(1,colcount+1,stock.getUnderlyingPrice())


'''
from Stock import *
import calendar
import pytz
s=Stock("aaa")
s.setUnderlyingPrice(12.34)
d = datetime.datetime(2018, 5, 18, 0, 0, 0, 0, tzinfo=pytz.timezone('GMT'))
timestamp = calendar.timegm(d.timetuple())
option = Option('AMZN', 'PUT', 1350, 1430.79, 19.5, 16.85, datetime.datetime.utcnow())
option.setExpirationDate(timestamp)
option.setApr()
option2 = Option('AMZN', 'PUT', 1300, 1430.79, 20.1, 17.40, datetime.datetime.utcnow())
option2.setExpirationDate(timestamp)
option2.setApr()
o=[option,option2]
GSW=GoogleSheetWriter()
GSW.connect()
GSW.write(s,o)


l = [i.__repr__().split() for i in o]
q = [item for sublist in l for item in sublist]
print(q)

#l=[item for s in o]
#flat_list = [item for sublist in o for item in split(sublist.__repr__())]
#pprint(flat_list)
'''