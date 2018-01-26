from bittrexStream import bittrexStream
import threading
import sys
import time

interval_sec=600

Bittrex_sql = bittrexStream(baseCurrency = 'BTC', db='bittrex.db')

def runPAIRS(interval=interval_sec):
    try:
        Bittrex_sql.updateDB()
        t=threading.Timer(interval, runPAIRS)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('Wird erneut gestartet...\n')
        runPAIRS()

def runPAIRS1():
    while True:
        try:
            Bittrex_sql.updateDB()
            time.sleep(interval_sec)
        except KeyboardInterrupt:
            break
        except:
            print("Fehler: ", sys.exc_info()[0])
            print('Wird erneut gestartet...\n')
            continue

#def main():

#if __name__ == '__main__':
#    main()
