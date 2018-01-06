from Polostream import Polostream
import threading
import sys
import requests

# specify the path to the database
path = 'PoloPercent.db'

# set up the main functions you want to stream

interval_sec=600

url = 'https://poloniex.com/public?command=returnTicker'
data = requests.get(url).json()

BTC_PAIRS = []
for f in data:
    if f[0:3]=='BTC':
        BTC_PAIRS.append(f)

Pairs_sql = Polostream(BTC_PAIRS,path)

def runPAIRS(interval=interval_sec):
    try:
        Pairs_sql.updateDB()
        t=threading.Timer(interval, runPAIRS)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('Wird erneut gestartet...\n')
        runPAIRS()

#def main():

#if __name__ == '__main__':
#    main()
