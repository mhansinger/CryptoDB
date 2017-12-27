from SQLstream import SQLstream
import threading
import sys

# specify the path to the database
path = 'ShitCoins.db'

# set up the main functions you want to stream

interval_sec=300

PIVXBTC_sql = SQLstream('ETH','BTC',path)
ETHEUR_sql = SQLstream('ETH','EUR',path)
BTCEUR_sql = SQLstream('BTC','EUR',path)
LTCEUR_sql = SQLstream('LTC','EUR',path)
LTCBTC_sql = SQLstream('LTC','BTC',path)
XMRBTC_sql = SQLstream('XMR','BTC',path)
DASHBTC_sql = SQLstream('DASH','BTC',path)
XRPBTC_sql = SQLstream('XRP','BTC',path)
STRBTC_sql = SQLstream('STR','BTC',path)
XEMBTC_sql = SQLstream('XEM','BTC',path)
STRATBTC_sql = SQLstream('STRAT','BTC',path)


def runETHBTC(interval=interval_sec):
    try:
        ETHBTC_sql.updateDB()
        t=threading.Timer(interval, runETHBTC)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHBTC wird erneut gestartet...\n')
        runETHBTC()

def main():



if __name__ == '__main__':
    main()
