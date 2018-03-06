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
        # check the index list
        index_list = []
        id_count = 0
        bittrex_coinlist = []
        # if Bittrex adds a new coin pari you would get an error in your database.
        # So, generate index_list of the current BTC-pairs from bittrex which are in your database
#         for i in range(0,len(data_all)):
#             if id_count < len(self.pairlist):
#                 if data_all[i]['MarketName'] == self.pairlist[id_count]:
#                     index_list.append(i)
#                     id_count += 1
#                 else:
#                     print('Coin pair is not in your database: ',data_all[i]['MarketName'])
#                     pass
        for i in range(0,len(data_all)):
            bittrex_coinlist.append(data_all[i]['MarketName'])
        
        # update the index list to iterate over in the next step
        index_list = [bittrex_coinlist.index(i) for i in bittrex_coinlist if i in self.pairlist]
        
        # independent counter for pairlist
        count = 0
        # loop over index_list, check again if the coin names are correct and then construct the string vectors
        # to be inserted into the sql database, kind of double check
        for idx in index_list:
            try:
                data_coin = data_all[idx]
                try:
                    assert data_coin['MarketName'] == self.pairlist[count]
                except AssertionError:
                    print('Somethings wrong with the coin order')

                price = data_coin['Last']
                volume = data_coin['BaseVolume']
                ask = data_coin['Ask']
                bid = data_coin['Bid']
            
            except:
                print('Coin is not listed anymore on Bittrex!')
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
            # do not add ',' to the last entry
            else:
                price_vec += str(price)
                volume_vec += str(volume)
                ask_vec += str(ask)
                bid_vec += str(bid)
                print(idx)
            # increase counter
            count += 1

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

