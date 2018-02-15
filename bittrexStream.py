import sqlite3
import time
import os.path
import requests


class bittrexStream(object):
    def __init__(self,baseCurrency = 'BTC', db='bittrex.db', url = 'https://bittrex.com/api/v1.1/public/getmarketsummaries'):
        '''
        Get % change from Bittrex
        '''
        self.url = url
        print(self.url)

        self.base = baseCurrency
        data = requests.get(self.url).json()
        self.pairs = []
        self.insert_price = None
        self.insert_volume = None
        self.insert_ask = None
        self.insert_bid = None

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

        self.col_vector = 'UNIX_Time,  ' + self.col_vector
        self.columns = 'UNIX_Time,  ' + self.pair_vector

        self.path = db

        # checks if the table in the database is already existing, otherwise creates a table
        if (os.path.exists(self.path)):
            print('Open table')
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            price_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_PRICE (UNIX_Time INT, ' + self.pair_vector + ')'
            volume_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_VOLUME (UNIX_Time INT, ' + self.pair_vector + ')'
            ask_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_ASK (UNIX_Time INT, ' + self.pair_vector + ')'
            bid_string = 'CREATE TABLE IF NOT EXISTS BTC_PAIRS_BID (UNIX_Time INT, ' + self.pair_vector + ')'
            #print(price_string)
            c.execute(price_string)
            c.execute(volume_string)
            c.execute(ask_string)
            c.execute(bid_string)
            conn.commit()
            conn.close()
        else:
            print("create your data base first!")

    def getTicker(self):
        # get the Data from poloniex
        try:
            data = requests.get(self.url).json()['result']
        except ValueError:
            print('There was a ValueError in getTicker')
            time.sleep(60)
            return self.getTicker()
        return data

    def updateDB(self):
        data_all = self.getTicker()
        price_vec = ''
        volume_vec = ''
        ask_vec = ''
        bid_vec = ''
        for idx, pair in enumerate(self.pairs):
            try:
                data_coin = data_all['result'][idx]

                try:
                    assert data_coin['MarketName'] == pair.replace('_','-')
                except AssertionError:
                    print('Somethings wrong with the coin order')

                price = data_coin['Last']
                volume = data_coin['BaseVolume']
                ask = data_coin['Ask']
                bid = data_coin['Bid']
            
            except:
                print(pair,' is not listed anymore on Bittrex!')
                price = 0.0
                volume = 0.0
                ask = 0.0
                bid = 0.0
                pass


            if idx < len(self.pairs)-1:
                price_vec += str(price)+','
                volume_vec += str(volume)+','
                ask_vec += str(ask)+','
                bid_vec += str(bid)+','
            else:
                price_vec += str(price)
                volume_vec += str(volume)
                ask_vec += str(ask)
                bid_vec += str(bid)
                print(idx)

        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())

        # connect to DB
        self.insert_price = "INSERT INTO BTC_PAIRS_PRICE (" + self.col_vector + ") " + " VALUES (" + str(unixtime) + "," + price_vec + ")"
        self.insert_volume = "INSERT INTO BTC_PAIRS_VOLUME (" + self.col_vector + ") " + " VALUES (" + str(unixtime) + "," + volume_vec + ")"
        self.insert_ask = "INSERT INTO BTC_PAIRS_ASK (" + self.col_vector + ") " + " VALUES (" + str(unixtime) + "," + ask_vec + ")"
        self.insert_bid = "INSERT INTO BTC_PAIRS_BID (" + self.col_vector + ") " + " VALUES (" + str(unixtime) + "," + bid_vec + ")"

        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute(self.insert_price)
        c.execute(self.insert_volume)
        c.execute(self.insert_ask)
        c.execute(self.insert_bid)
        conn.commit()
        conn.close()
        print('Update the data base at ' + str(date))

