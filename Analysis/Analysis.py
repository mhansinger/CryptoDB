# Analyse the BITTREX stream data

import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt


price = pd.read_csv('BTC_PAIRS_PRICE')
ask = pd.read_csv('BTC_PAIRS_ASK')
bid = pd.read_csv('BTC_PAIRS_BID')
volume = pd.read_csv('BTC_PAIRS_VOLUME')

# get the columns
pairs = list(volume.columns)
pairs = [p for p in pairs if p[0:3]=='BTC']

log_return = copy.copy(volume)

def rsiFunc(prices, n=60):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi



#Works

minute_shift=5
bought = False
buy_price = 0
invest = 100
trades = 0
lost = 0
badtrade = 0
exittime = 150
dropLimit=-0.025 #-0.026
gain=1.012
peak=0.012
badTradeList = []
badTradePos = []

log_return = price.copy()
for p in pairs:
    #ptc_change[p] = price[p].ptc_change()
    log_return[p] = np.log(ask[p]) - np.log(ask[p].shift(minute_shift))

def peak_check(i,thisList):
    maxDrop = log_return[thisList].iloc[i].min()
    maxDropCoin = log_return[thisList].iloc[i].idxmin()
    maxVolume = volume[maxDropCoin].iloc[i]
    if log_return[maxDropCoin].iloc[(i-10):i].max()>peak and maxDrop < dropLimit:
        #remove the 'bad' coin and run again the check
        newList = copy.copy(thisList)
        newList.remove(maxDropCoin)
        return peak_check(i,thisList=newList)
    else:
        #print(log_return[maxDropCoin].iloc[(i-60):i].max())
        return maxDrop, maxDropCoin, maxVolume

# analysis of all coins
thisCoin=None
#for i in range(20, len(log_return)-1):
for i in range(20, 14000):
    if bought is False:
        # NEW!!!
        # find first relevant Coins which fulfil VOL criteria, then check for drop in log return
        volList = []
        for loc, coin in enumerate(pairs):
            if volume[coin].iloc[-1] > 1000:
                volList.append(coin)

        maxDrop, maxDropCoin, maxVolume = peak_check(i,thisList=volList)

        if maxDrop<dropLimit:
            # if log_ETH.iloc[ind] < -0.0125

            # check the RSI
            # print('RSI is:')
            # print(rsiFunc(price[maxDropCoin],20))
            # print('')

            thisCoin = maxDropCoin
            coins = invest / ask[thisCoin].iloc[i]
            bought = True
            buy_price = ask[thisCoin].iloc[i]
            print(thisCoin)
            print(maxDrop)
            print('bought at: ', buy_price)
            print(i)
            buy_id = i
            trades += 1
            print('trades: ', trades)
            rolling = price[thisCoin].rolling(20).mean().iloc[i]
            print('Rolling mean: ', rolling)
            print(' ')
    elif bought:
        if bid[thisCoin].iloc[i] >= gain* buy_price or i > buy_id + exittime:
            invest = coins * bid[thisCoin].iloc[i]
            invest = invest * (1. - 0.005)
            print('sold at: ', bid[thisCoin].iloc[i])
            print('Investment is: ', invest)
            if i > buy_id + exittime and bid[thisCoin].iloc[i] < buy_price:
                badtrade += 1
                lost += coins * (buy_price - bid[thisCoin].iloc[i])
                print('Bad Trade!')
                print(thisCoin)
                print(log_return[thisCoin].iloc[(i-20-exittime):(i-exittime)].max())
                badTradeList.append(thisCoin)
                badTradePos.append(i-exittime)
            print(i)
            print(' ')
            # because we sold
            bought = False
            thisCoin = None

    #print(thisCoin)
print('bad trades %: ', (badtrade / trades) * 100)
print('Bad trades lost: ',lost)
print('Bad trade list: ',badTradeList)

for i in range(len(badTradeList)):
    plt.figure(i)
    plt.plot(price[badTradeList[i]],'k')
    plt.plot(ask[badTradeList[i]],'b:')
    plt.plot(bid[badTradeList[i]], 'b--')
    j = badTradePos[i]
    plt.plot(j,ask[badTradeList[i]].iloc[j],'g>')
    plt.plot(j+exittime, bid[badTradeList[i]].iloc[j+exittime], 'r>')
    plt.title(badTradeList[i])

plt.show()




#def RSI(i,volList):


''' 
#Works
minute_shift=5
bought = False
buy_price = 0
invest = 100
trades = 0
lost = 0
badtrade = 0
exittime = 150
dropLimit=-0.028 #-0.026
gain=1.014
peak=0.012
badTradeList = []
badTradePos = []

minute_shift=10
bought = False
buy_price = 0
invest = 100
trades = 0
lost = 0
badtrade = 0
exittime = 150
dropLimit=-0.03 #-0.026
gain=1.014
peak=0.012

# mit limit auf 1000 btc
minute_shift=4
bought = False
buy_price = 0
invest = 100
trades = 0
lost = 0
badtrade = 0
exittime = 150
dropLimit=-0.03 #-0.026
gain=1.012
peak=0.01
badTradeList = []
badTradePos = []

minute_shift=5
bought = False
buy_price = 0
invest = 100
trades = 0
lost = 0
badtrade = 0
exittime = 150
dropLimit=-0.03 #-0.026
gain=1.015
peak=0.012
badTradeList = []
badTradePos = []





XETH_series = pd.read_csv('XETHXXBT_Series.csv')

ETH_price2 = XETH_series.Price[14000:100000]


log_ETH = np.log(ETH_price2)-np.log(ETH_price2.shift(1))

#log_3 = np.zeros(len(log_ETH))
#log_2 = np.zeros(len(log_ETH))

#for i in range(2,len(log_ETH)):
#log_3 = log_ETH.rolling(30).sum()
#log_2 = log_ETH.rolling(20).sum()



bought = False
buy_price = 0
invest = 100
trades =0
badtrade = 0
lost=0
#buy_index = []
#sell_index = []

for ind, market in enumerate(ETH_price2):
    if bought is False:
        if log_ETH.iloc[ind] < -0.0125
            coins = invest / market
            bought = True
            buy_price = market
            print('bought at: ', buy_price)
            print(ind)
            buy_id=ind
            trades+=1
            print('trades: ',trades)

    elif bought:
        if market >= 1.013*buy_price or ind > buy_id+200:
            invest = coins * market
            invest = invest * (1. - 0.005)
            print('sold at: ', market)
            print('Investment is: ', invest)
            
            if ind > buy_id+exitsell and market < buy_price:
                badtrade+=1
                lost += coins*(buy_price-market)
            print(ind)
            print(' ')
            bought = False
    
print('bad trades %: ',(badtrade/trades)*100)

import scipy.stats as stats
import pylab

def qqplot(log):
    stats.probplot(log, dist="norm", plot=pylab)
    pylab.show()
            '''
# best is to use the 1 min log series with -1.5% and sell for a plus of 2%, exit after 200 min any way. check this with different series.