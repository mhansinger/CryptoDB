import sqlite3
import time
import os.path
import requests


class Polostream(object):
    def __init__(self, pairs = ['BTC_ETH','BTC_LTC'], db='TEST.db'):
        '''
        Get % change from Poloniex
        '''

        self.pairs = pairs
        self.pairs.sort()
        self.pair_vector = pairs[0] + ' REAL'
        for p in range(1,len(pairs)):
            self.pair_vector+=', '+ pairs[p] + ' REAL'

        self.col_vector=pairs[0]
        for p in range(1,len(pairs)):
            self.col_vector+=', '+ pairs[p]

        self.col_vector = 'UNIX_Time, Date, '+self.col_vector
        self.columns = 'UNIX_Time, Date, ' + self.pair_vector
        self.url = 'https://poloniex.com/public?command=returnTicker'
        self.path = db

        # checks if the table in the database is already existing, otherwise creates a table
        if (os.path.exists(self.path)):
            print('Open table')
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            percent_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_PERCENT (UNIX_Time INT, Date TEXT,'+self.pair_vector+')'
            price_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_PRICE (UNIX_Time INT, Date TEXT,' + self.pair_vector + ')'
            volume_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_VOLUME (UNIX_Time INT, Date TEXT,' + self.pair_vector + ')'
            #print(percent_string)
            #print(price_string)
            c.execute(percent_string)
            c.execute(price_string)
            c.execute(volume_string)
            conn.commit()
            conn.close()
        else:
            print("create your data base first!")

    def getTicker(self):
        # get the Data from poloniex
        data = requests.get(self.url).json()
        return data

    def updateDB(self):
        data_all = self.getTicker()
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        percent_vec=''
        price_vec = ''
        volume_vec =''
        for idx, pair in enumerate(self.pairs):
            data_coin = data_all[pair]
            percent = data_coin['percentChange']
            price = data_coin['last']
            volume = data_coin['baseVolume']

            if idx < len(self.pairs)-1:
                percent_vec +=percent+', '
                price_vec +=price+', '
                volume_vec +=volume+', '
            else:
                percent_vec +=percent
                price_vec +=price
                volume_vec += volume

        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())

        # connect to DB
        insert_percent = "INSERT INTO BTC_PAIRS_PERCENT (" + self.col_vector + ") " + " VALUES (" + str(
                unixtime) + ", '" + str(date)+ "' ," + percent_vec + ")"

        insert_price = "INSERT INTO BTC_PAIRS_PRICE (" + self.col_vector + ") " + " VALUES (" + str(
                unixtime) + ", '" + str(date)+ "' ," + price_vec + ")"
        insert_volume = "INSERT INTO BTC_PAIRS_VOLUME (" + self.col_vector + ") " + " VALUES (" + str(
                unixtime) + ", '" + str(date)+ "' ," + volume_vec + ")"

        print(insert_percent)
        #print(insert_price)
        c.execute(insert_percent)
        c.execute(insert_price)
        c.execute(insert_volume)
        conn.commit()
        print('Update the data base at ' + str(date))
        conn.close()

