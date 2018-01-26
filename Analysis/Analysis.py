import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt

percent = pd.read_csv('BTC_PAIRS_PERCENT')
price = pd.read_csv('BTC_PAIRS_PRICE')
volume = pd.read_csv('BTC_PAIRS_VOLUME')

# get the columns
pairs = list(percent.columns)
pairs = [p for p in pairs if p[0:3]=='BTC']

log_return = price.copy()
ptc_change = price.copy()

for p in pairs:
    #ptc_change[p] = price[p].ptc_change()
    log_return[p] = np.log(price[p]) - np.log(price[p].shift(1))


for i, p in enumerate(pairs):
    plt.figure(i)
    price[p].plot()
    plt.title(p)
    plt.figure(i+100)
    volume[p].plot()
    plt.title(p)
    plt.figure(i + 500)
    log_return[p].plot()
    plt.title(p)

plt.show(block=False)

log_BTC = percent['BTC_LTC']

price_LTC = price['BTC_LTC']



pair = 'BTC_ETH'

for p in pairs:
    log_3 = np.zeros(len(log_BTC))
    log_2 = np.zeros(len(log_BTC))
    for i in range(2, len(log_return[p])):
        log_3[i] = log_return[p].iloc[i - 2] + log_return[p].iloc[i - 1] + log_return[p].iloc[i]
        log_2[i] = log_return[p].iloc[i - 1] + log_return[p].iloc[i]

    bought = False
    buy_price = 0
    invest = 100

    for ind, market in enumerate(price[pair]):
        if log_3[ind] < -0.022 and bought is False:
            # we buy now
            coins = invest / market
            bought = True
            buy_price = market
            # print('bought at: ', buy_price)
            # print(ind)
            buy_id = ind

        if bought:
            if market >= 1.02 * buy_price or ind > buy_id + 20:
                invest = coins * market
                invest = invest * (1. - 0.004)
                # print('sold at: ', market)
                # print('Investment is: ', invest)
                bought = False
                # print(ind)
                # print(' ')
    print(' ')
    print(p)
    print(invest)
    print(' ')


bought = False
buy_price = 0
invest = 100
trades = 0
lost = 0
badtrade = 0
exit = 20

# analysis of all coins
for i in range(1, len(log_return)):
#for i in range(1,500):
    #print(log_return.iloc[i,2:-1].idxmin())
    #print(log_return.iloc[i,2:-1].min())

    maxDrop = log_return.iloc[i,2:-1].min()
    maxDropCoin = log_return.iloc[i,2:-1].idxmin()
    maxVolume = volume[maxDropCoin].iloc[i]

    if bought is False and maxDrop<-0.04 and maxVolume > 150:
        #if log_ETH.iloc[ind] < -0.0125
        thisCoin = maxDropCoin
        coins = invest / price[thisCoin].iloc[i]
        bought = True
        buy_price = price[thisCoin].iloc[i]
        print(log_return.iloc[i, 2:-1].idxmin())
        print(log_return.iloc[i, 2:-1].min())
        print('bought at: ', buy_price)
        print(i)
        buy_id = i
        trades += 1
        print('trades: ', trades)
        print(' ')
    elif bought:
        if price[thisCoin].iloc[i] >= 1.02 * buy_price or i > buy_id + exit:
            invest = coins * price[thisCoin].iloc[i]
            invest = invest * (1. - 0.005)
            print('sold at: ', price[thisCoin].iloc[i])
            print('Investment is: ', invest)
            if i > buy_id + exit and price[thisCoin].iloc[i] < buy_price:
                badtrade += 1
                lost += coins * (buy_price - price[thisCoin].iloc[i])
                print('Bad Trade!')
                print(thisCoin)
            print(i)
            print(' ')
            # because we sold
            bought = False
print('bad trades %: ', (badtrade / trades) * 100)


''' 
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

def qqplot():
    stats.probplot(log_ETH, dist="norm", plot=pylab)
    pylab.show()
            '''
# best is to use the 1 min log series with -1.5% and sell for a plus of 2%, exit after 200 min any way. check this with different series.