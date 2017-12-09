import sqlite3
import pandas as pd
import numpy as np
from poloniex import Poloniex
import gdax
import time
import os.path

class SQLstream(object):
    def __init__(self, asset1='ETH',asset2='BTC',db='TEST.db'):
        '''
        Object streams via ploniex and GDAX api
        :param asset1: 'ETH'
        :param asset2: 'BTC'
        Use the GDAX stream for ETH-EUR and BTC-EUR information, it's not provided on Poloniex
        '''

        self.asset1 = asset1
        self.asset2 = asset2
        self.polo = Poloniex()
        self.GDAX = gdax.PublicClient()
        self.pair = asset2+'_'+asset1
        self.columns = 'UNIX_Time, Date, Price, Volume'
        #self.__history = pd.DataFrame([np.zeros(len(self.__columns))], columns=self.__columns)
        self.tablename = self.pair
        self.path = db

        if self.asset1 or self.asset2 == 'EUR' or 'USD' :
            print('')
        print(self.asset1)
        print(self.asset2)

        # checks if the table in the database is already existing, otherwise creates a table
        if (os.path.exists(self.path)):
            print('Open table')
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            table_string = 'CREATE TABLE IF NOT EXISTS '+self.tablename+' (UNIX_Time INT, Date TEXT, Price REAL, Volume REAL)'
            c.execute(table_string)
            conn.commit()
            conn.close()
        else:
            print("create data base!")

    def getTicker(self):
        # get the Data from poloniex
        ticker = self.polo.returnTicker()[self.pair]
        return ticker

    def getTickerGDAX(self):
        # this is a work around as Poloniex does not provide Tickers for EUR
        # Data is streamed from GDAX exchange
        ticker=self.GDAX.get_product_ticker(product_id=self.asset1+'-'+self.asset2)
        return ticker

    def updateDB(self):
        # fetch ticker data
        try:
            ticker = self.getTicker()
        except:
            print('Check if the pair is available on the exchange!')
        price = ticker['last']
        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())
        thisVolume = ticker['baseVolume']
        # connect to DB
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        insert_string = "INSERT INTO "+self.tablename+"("+self.columns+") "+" VALUES ("+ str(unixtime)+", '" + str(date)+ "' ," + str(price) + ","+str(thisVolume)+")"
        c.execute(insert_string)
        conn.commit()
        conn.close()
        print('Update '+str(self.pair)+' at '+str(date))

    def updateDB_GDAX(self):
        # this is for the data you get from GDAX! use only for USD and EUR in the BTC and ETH Market
        # fetch ticker data
        try:
            ticker = self.getTickerGDAX()
        except:
            print('Check if the pair is available on the exchange!')
        price = round(float(ticker['price']),3)
        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())
        thisVolume = round(float(ticker['volume']),3)
        # connect to DB
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        insert_string = "INSERT INTO "+self.tablename+"("+self.columns+") "+" VALUES ("+ str(unixtime)+", '" + str(date)+ "' ," + str(price) + ","+str(thisVolume)+")"
        c.execute(insert_string)
        conn.commit()
        conn.close()
        print('Update '+str(self.pair)+' at '+str(date))