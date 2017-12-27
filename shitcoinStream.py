import sqlite3
import time
import os.path
import requests


class SQLstream(object):
    def __init__(self, shitcoins=['ETH'],base='BTC',db='TEST.db'):
        '''
        Object streams via Bittrex API
        :param asset1: 'ETH'
        :param asset2: 'BTC'

        '''

        self.shitcoins = shitcoins # string vector#asset1
        self.base = base
        #self.pair = asset2+'-'+asset1
        self.columns = 'UNIX_Time, Date, Price, BaseVol, OpenBuy, OpenSell'
        #self.__history = pd.DataFrame([np.zeros(len(self.__columns))], columns=self.__columns)
        self.url = 'https://bittrex.com/api/v1.1/public/getmarketsummary?market=btc-'
        self.path = db

        # checks if the table in the database is already existing, otherwise creates a table
        if (os.path.exists(self.path)):
            print('Open table')
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            for coin in self.shitcoins:
                tablename= coin + '_' + self.base
                table_string = 'CREATE TABLE IF NOT EXISTS ' + tablename + \
                               ' (UNIX_Time INT, Date TEXT, Price REAL, BaseVol REAL, OpenBuy INT, OpenSell INT)'
                c.execute(table_string)
                conn.commit()
            conn.close()
        else:
            print("create data base!")

    def getTicker(self,coin):
        # get the Data from poloniex
        ticker = requests.get(self.url+coin).json()
        return ticker['result'][0]

    def updateDB(self):
        # fetch ticker data
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        for coin in self.shitcoins:
            ticker = self.getTicker(coin)
            price = ticker['Last']
            date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
            unixtime = int(time.time())
            thisVolume = ticker['BaseVolume']
            openBuy = ticker['OpenBuyOrders']
            openSell = ticker['OpenSellOrders']
            tablename = coin + '_' + self.base
            # connect to DB
            insert_string = "INSERT INTO " + tablename + "(" + self.columns + ") " + " VALUES (" + str(
                unixtime) + ", '" + str(date)+ "' ," + str(price) + ", " + str(thisVolume) + ", " + str(
                openBuy) + ", " + str(openSell) + ")"
            c.execute(insert_string)
            conn.commit()
            print('Update ' + str(tablename) + ' at ' + str(date))
        conn.close()

