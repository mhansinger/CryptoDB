import sqlite3
import time
import os.path
import requests


class bittrexStream(object):
    def __init__(self, baseCurrency = 'BTC', db='bittrex.db', url = 'https://bittrex.com/api/v1.1/public/getmarketsummaries'):
        '''
        Get % change from Bittrex
        '''
        self.url = url
        print(self.url)

        self.base = baseCurrency
        data = requests.get(self.url).json()
        self.pairs = []
        self.pairlist = []
        self.insert_price = None
        self.insert_volume = None
        self.insert_ask = None
        self.insert_bid = None

        # fill up the pairs to stream, according to base currency
        for p in range(len(data['result'])):
            thispair = data['result'][p]['MarketName']
            if thispair[0:3] == self.base:
                # this replacement has to be done for the sqlite database...
                self.pairlist.append(thispair)
                thispair = thispair.replace('-','_')
                print(thispair)
                self.pairs.append(thispair)

        self.pair_vector = self.pairs[0] + ' REAL'
        for p in range(1,len(self.pairs)):
            self.pair_vector += ', '+ self.pairs[p] + ' REAL'

        self.col_vector=self.pairs[0]
        for p in range(1,len(self.pairs)):
            self.col_vector += ', '+ self.pairs[p]

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
        # fetch the data from the exchange
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
        bittrex_coinlist = []
        index_list = []
        # if Bittrex adds a new coin pari you would get an error in your database.
        # So, generate index_list of the current BTC-pairs from bittrex which are in your database

        for i in range(0,len(data_all)):
            bittrex_coinlist.append(data_all[i]['MarketName'])

        # update the index list
        for coin in self.pairlist:
            try:
                index_list.append(bittrex_coinlist.index(coin))
            except ValueError:
                print('Coin is not listed anymore\n')

        # This is important: check whether self.index_list >= bittrex_coinlist
        # if True: more BTC coin pairs from bittrex than initially in our database -> reduce to these in our DB
        # if False: more BTC coin pairs in database than bittrex delivers (they removed some coins, but we still need
        # to provide numeric values for our database and create a consistent value vector)

        if len(index_list) >= len(self.pairlist):
            # loop over index_list, check again if the coin names are correct and then construct the string vectors
            # to be inserted into the sql database, kind of double check
            for i, idx in enumerate(index_list):
                data_coin = data_all[idx]

                try:
                    # check again, if the names match
                    assert data_coin['MarketName'] == self.pairlist[i]

                    price = data_coin['Last']
                    volume = data_coin['BaseVolume']
                    ask = data_coin['Ask']
                    bid = data_coin['Bid']

                except AssertionError:
                    print('Somethings wrong with the coin order')
                    price = 0
                    volume = 0
                    ask = 0
                    bid = 0

                if i < len(self.pairlist) - 1:
                    price_vec += str(price) + ','
                    volume_vec += str(volume) + ','
                    ask_vec += str(ask) + ','
                    bid_vec += str(bid) + ','
                else:
                    # do not add ',' to the last entry
                    price_vec += str(price)
                    volume_vec += str(volume)
                    ask_vec += str(ask)
                    bid_vec += str(bid)
                    print(idx)

        else:
            # this is the case when our list is longer than the BTC Coin list from bittrex
            print('\nBittrex reduced BTC pairs')
            # use the first index as counter; this should be 0 in case of BTC, however, in case of ETH as base currency
            # this index starts with ~200
            count = index_list[0]
            for i, coin in enumerate(self.pairlist):
                data_coin = data_all[count]
                try:
                    # check again, if the names match
                    assert data_coin['MarketName'] == coin
                    price = data_coin['Last']
                    volume = data_coin['BaseVolume']
                    ask = data_coin['Ask']
                    bid = data_coin['Bid']
                    count += 1
                except AssertionError:
                    print('%s has been removed from Bittrex\n' % coin)
                    price = 0
                    volume = 0
                    ask = 0
                    bid = 0

                if i < len(self.pairlist) - 1:
                    price_vec += str(price) + ','
                    volume_vec += str(volume) + ','
                    ask_vec += str(ask) + ','
                    bid_vec += str(bid) + ','
                else:
                    # do not add ',' to the last entry
                    price_vec += str(price)
                    volume_vec += str(volume)
                    ask_vec += str(ask)
                    bid_vec += str(bid)
                    print(i)


        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())

        # string vectors to update the sql database
        self.insert_price = "INSERT INTO BTC_PAIRS_PRICE (" + self.col_vector + ") " + " VALUES (" + str(unixtime) + "," + price_vec + ")"
        self.insert_volume = "INSERT INTO BTC_PAIRS_VOLUME (" + self.col_vector + ") " + " VALUES (" + str(unixtime) + "," + volume_vec + ")"
        self.insert_ask = "INSERT INTO BTC_PAIRS_ASK (" + self.col_vector + ") " + " VALUES (" + str(unixtime) + "," + ask_vec + ")"
        self.insert_bid = "INSERT INTO BTC_PAIRS_BID (" + self.col_vector + ") " + " VALUES (" + str(unixtime) + "," + bid_vec + ")"

        # connect to DB
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute(self.insert_price)
        c.execute(self.insert_volume)
        c.execute(self.insert_ask)
        c.execute(self.insert_bid)
        conn.commit()
        conn.close()
        print('Update the data base at ' + str(date))

