import sqlite3
import time
import os.path
import requests


class bittrexStream(object):
    def __init__(self,baseCurrency = 'BTC', db='bittrex.db'):
        '''
        Get % change from Poloniex
        '''
        self.url = 'https://bittrex.com/api/v1.1/public/getmarketsummaries'
        print(self.url)

        self.base = baseCurrency
        data = requests.get(self.url).json()
        self.pairs = []

        # fill up the pairs to stream, accroding to base currency
        for p in range(len(data['result'])):
            thispair= data['result'][p]['MarketName']
            if thispair[0:3] == self.base:
                # this replacement has to be done for the sqlite database...
                thispair=thispair.replace('-','_')
                print(thispair)
                self.pairs.append(thispair)

        self.pair_vector = self.pairs[0] + ' REAL'
        for p in range(1,len(self.pairs)):
            self.pair_vector+=', '+ self.pairs[p] + ' REAL'

        self.col_vector=self.pairs[0]
        for p in range(1,len(self.pairs)):
            self.col_vector+=', '+ self.pairs[p]

        self.col_vector = 'UNIX_Time, Date, ' + self.col_vector
        self.columns = 'UNIX_Time, Date, ' + self.pair_vector

        self.path = db

        # checks if the table in the database is already existing, otherwise creates a table
        if (os.path.exists(self.path)):
            print('Open table')
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            price_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_PRICE (UNIX_Time INT, Date TEXT,' + self.pair_vector + ')'
            volume_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_VOLUME (UNIX_Time INT, Date TEXT,' + self.pair_vector + ')'
            #print(price_string)
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
        price_vec = ''
        volume_vec =''
        for idx, pair in enumerate(self.pairs):
            data_coin = data_all['result'][idx]
            try:
                assert data_coin['MarketName'] == pair.replace('_','-')
            except AssertionError:
                print('Somethings wrong with the coin order')

            price = data_coin['Last']
            volume = data_coin['BaseVolume']

            if idx < len(self.pairs)-1:
                price_vec += str(price)+', '
                volume_vec += str(volume)+', '
            else:
                price_vec += str(price)
                volume_vec += str(volume)

        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())

        # connect to DB
        insert_price = "INSERT INTO BTC_PAIRS_PRICE (" + self.col_vector + ") " + " VALUES (" + str(
                unixtime) + ", '" + str(date)+ "' ," + price_vec + ")"
        insert_volume = "INSERT INTO BTC_PAIRS_VOLUME (" + self.col_vector + ") " + " VALUES (" + str(
                unixtime) + ", '" + str(date)+ "' ," + volume_vec + ")"

        c.execute(insert_price)
        c.execute(insert_volume)
        conn.commit()
        print('Update the data base at ' + str(date))
        conn.close()

