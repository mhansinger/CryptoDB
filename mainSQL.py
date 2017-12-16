from SQLstream import SQLstream
import threading
import sys

# specify the path to the database
path = 'Crypto.db'

# set up the main functions you want to stream

ETHBTC_sql = SQLstream('ETH','BTC',path)
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


def runETHBTC(interval=60):
    try:
        ETHBTC_sql.updateDB()
        t=threading.Timer(interval, runETHBTC)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHBTC wird erneut gestartet...\n')
        runETHBTC()

def runETHEUR(interval=60):
    try:
        ETHEUR_sql.updateDB_GDAX()
        t=threading.Timer(interval, runETHEUR)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runETHEUR()

def runBTCEUR(interval=60):
    try:
        # here gdax is neede
        BTCEUR_sql.updateDB_GDAX()
        t=threading.Timer(interval, runBTCEUR)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runBTCEUR()

def runLTCEUR(interval=60):
    try:
        LTCEUR_sql.updateDB_GDAX()
        t=threading.Timer(interval, runLTCEUR)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runLTCEUR()

def runLTCBTC(interval=60):
    try:
        LTCBTC_sql.updateDB()
        t=threading.Timer(interval, runLTCBTC)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runLTCBTC()

def runXMRBTC(interval=60):
    try:
        XMRBTC_sql.updateDB()
        t=threading.Timer(interval, runXMRBTC)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runXMRBTC()

def runDASHBTC(interval=60):
    try:
        DASHBTC_sql.updateDB()
        t=threading.Timer(interval, runDASHBTC)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runDASHBTC()

def runXRPBTC(interval=60):
    try:
        XRPBTC_sql.updateDB()
        t=threading.Timer(interval, runXRPBTC)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runXRPBTC()

def runXEMBTC(interval=60):
    try:
        XEMBTC_sql.updateDB()
        t=threading.Timer(interval, runXEMBTC)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runXEMBTC()

def runSTRATBTC(interval=60):
    try:
        STRATBTC_sql.updateDB()
        t=threading.Timer(interval, runSTRATBTC)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('ETHZEUR wird erneut gestartet...\n')
        runSTRATBTC()

def main():
    runETHBTC()
    runETHEUR()
    runBTCEUR()
    runLTCBTC()
    runLTCEUR()
    runXMRBTC()
    runDASHBTC()
    runXRPBTC()
    runXEMBTC()
    runSTRATBTC()


if __name__ == '__main__':
    main()
