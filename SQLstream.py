import sqlite3
import pandas as pd
import numpy as np
import krakenex
import time
import os.path

class SQLstream(object):
    def __init__(self, asset1,asset2,db='TEST.db'):
        '''
        Object streamt über krakenex.API die aktuellen Marktpreise
        :param asset1: 'XETH'
        :param asset2: 'XXBT'
        '''

        self.__asset1 = asset1
        self.__asset2 = asset2
        self.__k = krakenex.API()
        self.__pair = asset1 + asset2
        self.columns = 'UNIX_Time, Date, Price, Volume'
        #self.__history = pd.DataFrame([np.zeros(len(self.__columns))], columns=self.__columns)
        self.tablename = self.__pair
        self.__path = db

        print(self.__asset1)
        print(self.__asset2)

        # checks if the table in the database is already existing, otherwise creates a table
        if (os.path.exists(self.__path)):
            print('Open table')
            conn = sqlite3.connect(self.__path)
            c = conn.cursor()
            table_string = 'CREATE TABLE IF NOT EXISTS '+self.tablename+' (UNIX_Time INT, Date TEXT, Price REAL, Volume REAL)'
            c.execute(table_string)
            conn.commit()
            conn.close()
        else:
            print("create data base!")

    def market_price(self):
        market = self.__k.query_public('Ticker', {'pair': self.__pair})['result'][self.__pair]['c']
        return float(market[0])

    def getVolume(self):
        # gets the last 60 sec trading volume
        volume = self.__k.query_public('OHLC',{'pair': self.__pair})['result'][self.__pair][-1][-2]
        return float(volume)

    def updateDB(self):
        price = self.market_price()
        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())
        thisVolume = self.getVolume()
        # connect to DB
        conn = sqlite3.connect(self.__path)
        c = conn.cursor()
        insert_string = "INSERT INTO "+self.tablename+"("+self.columns+") "+" VALUES ("+ str(unixtime)+", '" + str(date)+ "' ," + str(price) + ","+str(thisVolume)+")"
        c.execute(insert_string)
        conn.commit()
        conn.close()
