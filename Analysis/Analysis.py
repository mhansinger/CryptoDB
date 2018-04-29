# Analyse the BITTREX stream data
import sqlite3
import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt

from numba import jit

SMALL = 1e-15
############################################
# get the data from the sqlite database

#conn = sqlite3.connect('bittrex.db')
#price = pd.read_sql("SELECT * FROM BTC_PAIRS_PRICE;",conn)
#ask = pd.read_sql("SELECT * FROM BTC_PAIRS_ASK;",conn)
#bid = pd.read_sql("SELECT * FROM BTC_PAIRS_BID;",conn)
#volume = pd.read_sql("SELECT * FROM BTC_PAIRS_VOLUME;",conn)
#conn.close()
############################################
price = pd.read_csv('BTC_PAIRS_PRICE.csv')
ask = pd.read_csv('BTC_PAIRS_ASK.csv')
bid = pd.read_csv('BTC_PAIRS_BID.csv')
volume = pd.read_csv('BTC_PAIRS_VOLUME.csv')

############################################

# get the columns, only consider BTC pairs
pairs_all = list(volume.columns)
pairs = [p for p in pairs_all if p[0:3] == 'BTC']

# Remove ZCL
pairs.remove('BTC_ZCL')

############################################
# replace 0.0 values in the data with previous one (n-1):
for p in pairs:
    price[p] = price[p].replace(to_replace=0,method='ffill')
    volume[p] = volume[p].replace(to_replace=0, method='ffill')
    bid[p] = bid[p].replace(to_replace=0, method='ffill')
    ask[p] = ask[p].replace(to_replace=0, method='ffill')


def rsiFunc(prices, index, n = 60):
    # computes the RSI over 60 min
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

    return rsi[index]


###########################
#Parameters to be tuned!
minute_shift = 8

exittime = 500
dropLimit = -0.029  #-0.026
dropLimit_low = -0.1
gain = 1.012
peak = 0.015
maxloss = 0.96
coinVolume = 700
blockingTime = 20      # hours
###########################


def peak_check(i,thisList,dropLimit_low,peak,block_coin,log_return):
    # checks if in the last 10 min a peak of 1% occured
    try:
        maxDrop = log_return[thisList].iloc[i].min()
        maxDropCoin = log_return[thisList].iloc[i].idxmin()
        maxVolume = volume[maxDropCoin].iloc[i]

        if log_return[maxDropCoin].iloc[(i - 20):i].max() > peak and maxDrop < dropLimit and maxDrop > dropLimit_low:
            # remove the 'bad' coin and run again the check
            newList = copy.copy(thisList)
            newList.remove(maxDropCoin)
            return peak_check(i, thisList=newList, dropLimit_low=dropLimit_low, peak=peak, block_coin=block_coin,log_return=log_return)
        else:
            # this is to check if the coin recently caused a BAD TRADE
            if maxDropCoin in block_coin.Coin.values or maxDrop < dropLimit_low:
                newList = copy.copy(thisList)
                newList.remove(maxDropCoin)
                return peak_check(i, thisList=newList, dropLimit_low=dropLimit_low, peak=peak, block_coin=block_coin,log_return=log_return)
            else:
                return maxDrop, maxDropCoin, maxVolume
    except ValueError:
        # in case of an error return sth. which will not cause a buy order:
        print('ValueError in peak check ...')
        return 0.0, 'BTC-ETH', 100


###########################
# backtesting analysis
# MAIN function

def run_analysis(exittime=exittime, dropLimit=dropLimit, dropLimit_low=dropLimit_low,gain=gain,peak=peak,
                 maxloss=maxloss,coinVolume=coinVolume, blockingTime=blockingTime,minute_shift=minute_shift):
    # reset some parameters
    buy_price = 0
    trades = 0
    lost = 0
    badtrade = 0
    badTradeList = []
    goodTradeList = []
    badTradePos = []
    trade_time = []
    bought = False
    invest = 100
    ############################
    # feature Engineering, name the features
    # IMPORTANT! It has to be consistent with the 'write_features' function (see below)!
    feature_list = ['id', 'Coin', 'logsum_60', 'logsum_180', 'minlog_30', 'maxlog_30',
                    'ratio_roll_30', 'ratio_roll_60', 'std_30', 'std_60', 'vol_30',
                    'vol_60', 'label']
    features_df = pd.DataFrame(np.zeros((1, len(feature_list))))
    features_df.columns = feature_list

    # create a log_return data frame from volume, to be filled later
    ############################
    global log_return
    log_return = price.copy()
    for p in pairs:
        # computes the log returns based on the minute_shift
        log_return[p] = np.log(ask[p]) - np.log(ask[p].shift(minute_shift))

    log_return = log_return.fillna(0)
    log_return = log_return.replace('-inf', 0.0)

    ############################

    block_coin = pd.DataFrame(columns=['UNIX','Pair'])
    block_coin = block_coin.append({'UNIX': 0, 'Coin': '-'}, ignore_index=True)

    # this runs the analysis, simulated trading
    thisCoin = None
    # for i in range(20, 14000):
    for i in range(20, len(log_return) - 1):
        if bought is False:
            # NEW!!!
            # find first relevant Coins which fulfil VOL criteria, then check for drop in log return
            volList = []
            for loc, coin in enumerate(pairs):
                if volume[coin].iloc[i] > coinVolume:
                    volList.append(coin)

            # do the peak check stuff and get the appropriate coins
            delta = i - 60*blockingTime
            block_coin = block_coin[block_coin.UNIX > delta]

            maxDrop, maxDropCoin, maxVolume = \
                peak_check(i, thisList=volList,dropLimit_low=dropLimit_low,peak=peak, block_coin=block_coin, log_return=log_return)

            #print(maxDrop, maxDropCoin, maxVolume)

            if maxDrop < dropLimit:  # and maxDrop > dropLimit_low:

                thisCoin = maxDropCoin
                coins = invest / ask[thisCoin].iloc[i]
                bought = True
                buy_price = ask[thisCoin].iloc[i]
                print(thisCoin)
                print(maxDrop)
                print('bought at: ', buy_price)
                print('Volume: ', maxVolume)
                print(i)
                buy_id = i
                trades += 1
                print('trades: ', trades)
                rolling = price[thisCoin].rolling(30).mean().iloc[i]
                print('Rolling mean: ', round(rolling, 5))
                print(' ')

        elif bought:
            if (bid[thisCoin].iloc[i] >= gain * buy_price or i > buy_id + exittime or \
                    bid[thisCoin].iloc[i] < buy_price * maxloss) and bid[thisCoin].iloc[i] > 0.0:
                invest = coins * bid[thisCoin].iloc[i]
                invest = invest * (1. - 0.005)
                print('sold at: ', bid[thisCoin].iloc[i])
                print('Investment is: ', invest)
                if bid[thisCoin].iloc[i] < buy_price:  # and i > buy_id + exittime:
                    badtrade += 1
                    lost += coins * (buy_price - bid[thisCoin].iloc[i])
                    print('Bad Trade!')
                    print(thisCoin)
                    # print(log_return[thisCoin].iloc[(i-10-exittime):(i-exittime)].max())
                    badTradeList.append(thisCoin)
                    badTradePos.append(i - exittime)
                    # UPDATE the FEATURE MATRIX
                    features_df = writeFeatures(idx_buy = buy_id,label=0, features=features_df,coin=thisCoin,log_return=log_return)

                    # update bad trade list
                    block_coin = block_coin.append({'UNIX':i,'Coin':thisCoin},ignore_index=True)

                else:
                    # good trade
                    features_df = writeFeatures(idx_buy = buy_id,label=1, features=features_df,coin=thisCoin,log_return=log_return)
                    trade_time.append(i - buy_id)
                    goodTradeList.append(thisCoin)

                print(i)
                print(' ')
                # because we sold
                bought = False
                thisCoin = None

        # print(thisCoin)
    print('bad trades %: ', round((badtrade / (trades + SMALL)) * 100, 2))
    print('Bad trades lost: ', round(lost, 2))
    print('Bad trade list: ', badTradeList)
    print('Good trade list: ', goodTradeList)
    print('Good trade time:', trade_time)

    return features_df

###########################

#features_df=run_analysis(exittime=exittime, dropLimit=dropLimit, dropLimit_low=dropLimit_low,gain=gain,peak=peak,
#                         maxloss=maxloss,coinVolume=coinVolume,blockingTime=blockingTime)


def writeFeatures(idx_buy,label,features ,coin,log_return):
    '''
    This function writes all selected features into a matrix
    logsum_30: cumulative log return over 30 min
    logsum_60: cumulative log return over 60 min
    logsum_180: cumulative log return over 180 min
    minlog_30: minimum log return in the last 30 min
    maxlog_30: maximum log return in the last 30 min
    ratio_roll_30: ratio of 30 min rolling mean to buy price
    ratio_roll_60: ratio of 60 min rolling mean to buy price
    std_30: rolling standard deviation over 30 min
    std_60: rolling standard deviation over 60 min
    vol_30: ratio of current trading vol to 30 min rolling
    vol_60: ratio of current trading vol to 60 min rolling
    RSI_60: RSI of ask price
    j:      Index where the coin was bought
    label:  1 for successful trade, 0 for fail trade
    '''
    #print('WRITE FEATURES')
    j=idx_buy
    #logsum_30 = log_return[coin].iloc[j-30:j].sum()
    logsum_60 = log_return[coin].iloc[j - 60:j].sum()
    logsum_180 = log_return[coin].iloc[j - 180:j].sum()
    minlog_30 = log_return[coin].iloc[j - 30:j].min()
    maxlog_30 = log_return[coin].iloc[j - 30:j].max()
    ratio_roll_30 = ask[coin].iloc[j]/ask[coin].rolling(30).mean().iloc[j] -1.
    ratio_roll_60 = ask[coin].iloc[j]/ask[coin].rolling(60).mean().iloc[j] -1.
    std_30 = ask[coin].rolling(30).std().iloc[j]/ask[coin].rolling(30).mean().iloc[j]
    std_60 = ask[coin].rolling(60).std().iloc[j]/ask[coin].rolling(60).mean().iloc[j]
    vol_30 = volume[coin].iloc[j]/volume[coin].rolling(30).mean().iloc[j] -1.
    vol_60 = volume[coin].iloc[j]/volume[coin].rolling(60).mean().iloc[j] -1.
    #RSI_60 = rsiFunc(ask[coin],index=j,n=60)
    return features.append({'id':j,'Coin':coin,'logsum_60':logsum_60 ,'logsum_180':logsum_180 ,
                            'minlog_30':minlog_30 ,'maxlog_30':maxlog_30,'ratio_roll_30':ratio_roll_30 ,
                            'ratio_roll_60':ratio_roll_60 ,'std_30':std_30 ,'std_60':std_60 ,'vol_30':vol_30,
                                    'vol_60':vol_60,'label':label},ignore_index=True)


################################
# Machine Learning

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

#scaler = MinMaxScaler()    # besser nicht scalen, sollte eh alles zw 0 und 1 sein
def fit_RF(features_df):

    clf = RandomForestClassifier()

    y = features_df['label'].values
    X = features_df.drop(['id', 'Coin', 'label'], axis=1).values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

    clf.fit(X_train, y_train)
    print('classifier score: ',clf.score(X_test, y_test))
    print(y_test)
    print(clf.predict(X_test))


def plot_logreturn(log_return=log_return,limit = dropLimit):
    below = 0
    data_zero=np.zeros(shape=(1,len(pairs)))
    global log_data
    log_data = pd.DataFrame(data_zero,columns=log_return[pairs].columns.values)
    for p in pairs:
        plt.scatter(log_return.index.values,log_return[p], s=0.3, c='k')
        low = log_return[p][log_return[p]<dropLimit]
        below += len(low)
        log_data[p] = len(low)
        plt.scatter(low.index.values,low, s=0.3, c='r')
    plt.figure()
    log_data.plot(kind='bar')
    plt.show(block=False)
    print('Below: ',below)
    print('Percentage: ', below/(len(pairs)*len(log_return)))


def plot_hist(log_return=log_return):
    log_return_np = log_return[pairs].values
    log_return_np = log_return_np.reshape(log_return_np.shape[0]*log_return_np.shape[1])
    plt.hist(log_return_np,bins=100)
    plt.show(block=False)



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
dropLimit=-0.03 #-0.026
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



# plot all the log returns
dropLimit=-0.025
count=0
drop_list=[]
fail_list = []
log_return_all=[]
plt.figure(100)
invest=100




for i in range(len(price)):
    plt.figure(i)
    plt.plot(price[badTradeList[i]],'k')
    plt.plot(ask[badTradeList[i]],'b:')
    plt.plot(bid[badTradeList[i]], 'b--')
    j = badTradePos[i]
    plt.plot(j,ask[badTradeList[i]].iloc[j],'g>')
    plt.plot(j+exittime, bid[badTradeList[i]].iloc[j+exittime], 'r>')
    plt.title(badTradeList[i])

plt.show(block=False)   


for p in pairs:
    #ptc_change[p] = price[p].ptc_change()
    plt.plot(log_return[p],'.k')
    log_return_all.insert(-1,list(log_return[p].values))
    can_buy = 0
    #for i in range(0,len(log_return[p])):
    for i in range(0, 14000):
        if log_return[p][i] < dropLimit and volume[p][i]>200 and log_return[p].iloc[(i-10):i].max()<peak:
            plt.plot(i,log_return[p][i], '.r')
            count+=1
            drop_list.append(p)
            if i>=can_buy:
                can_buy = i + exittime
                if any(bid[p][i + 1:(i + exittime)] > ask[p][i] * gain):
                    #invest = (invest * 0.995) * gain
                    print('Success')

                else:
                    print('Fail: ', p)
                    #invest = (invest) * min((bid[p][i] / ask[p][i + exittime]),1.) * 0.995
                    #fail_list.append(p)

        elif log_return[p][i] < dropLimit:
            plt.plot(i,log_return[p][i], '.b')

print('Invest is: ',invest)
plt.title('2 min log-return of all coins')

plt.show(block=False)


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

 best is to use the 1 min log series with -1.5% and sell for a plus of 2%, exit after 200 min any way. check this with different series.

'''