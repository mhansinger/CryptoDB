from shitcoinStream import SQLstream
import threading
import sys

# specify the path to the database
path = 'ShitCoins.db'

# set up the main functions you want to stream

interval_sec=600

# which shit coins to stream
coins = ['ETH','PIVX','NEO','COVAL','NXT','SALT','DGB','RDD','FCT','VTC','ENG','NMR']

Shitcoins_sql = SQLstream(shitcoins=coins,base='BTC',db=path)

def runShitCoins(interval=interval_sec):
    try:
        Shitcoins_sql.updateDB()
        t=threading.Timer(interval, runShitCoins)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHBTC wird erneut gestartet...\n')
        runShitCoins()


