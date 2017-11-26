from SQLstream import SQLstream

# set up the main functions you want to stream

XETHXXBT_sql = SQLstream('XETH','XXBT','Crypto.db')
XETHZEUR_sql = SQLstream('XETH','ZEUR','Crypto.db')
XXBTZEUR_sql = SQLstream('XXBT','ZEUR','Crypto.db')
XLTCZEUR_sql = SQLstream('XLTC','ZEUR','Crypto.db')
XLTCXXBT_sql = SQLstream('XLTC','XXBT','Crypto.db')
XXMRXXBT_sql = SQLstream('XXMR','XXBT','Crypto.db')
XXMRZEUR_sql = SQLstream('XXMR','ZEUR','Crypto.db')
XZECZEUR_sql = SQLstream('XZEC','ZEUR','Crypto.db')
XICNXXBT_sql = SQLstream('XICN','XXBT','Crypto.db')
DASHXXBT_sql = SQLstream('DASH','XXBT','Crypto.db')
DASHZEUR_sql = SQLstream('DASH','ZEUR','Crypto.db')


def run1(interval=60):
    try:
        XETHXXBT_sql.updateDB()
        t=threading.Timer(interval, run1)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHXXBT wird erneut gestartet...\n')
        run1()

def run2(interval=60):
    try:
        XETHZEUR_sql.updateDB()
        t=threading.Timer(interval, run2)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run2()

def run3(interval=60):
    try:
        XXBTZEUR_sql.updateDB()
        t=threading.Timer(interval, run3)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run3()

def run4(interval=60):
    try:
        XLTCZEUR_sql.updateDB()
        t=threading.Timer(interval, run4)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run4()

def run5(interval=60):
    try:
        XLTCXXBT_sql.updateDB()
        t=threading.Timer(interval, run5)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run5()

def run6(interval=60):
    try:
        XXMRXXBT_sql.updateDB()
        t=threading.Timer(interval, run6)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run6()

def run7(interval=60):
    try:
        XXMRZEUR_sql.updateDB()
        t=threading.Timer(interval, run7)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run7()

def run8(interval=60):
    try:
        XZECZEUR_sql.updateDB()
        t=threading.Timer(interval, run8)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run8()

def run9(interval=60):
    try:
        XICNXXBT_sql.updateDB()
        t=threading.Timer(interval, run9)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run9()

def run10(interval=60):
    try:
        DASHXXBT_sql.updateDB()
        t=threading.Timer(interval, run10)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run10()

def run11(interval=60):
    try:
        DASHZEUR_sql.updateDB()
        t=threading.Timer(interval, run11)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('XETHZEUR wird erneut gestartet...\n')
        run11()

def main():
    run1()
    run2()
    run3()
    run4()
    run5()
    run6()
    run7()
    run8()
    run9()
    run10()
    run11()

if __name__ == '__main__':
    main()