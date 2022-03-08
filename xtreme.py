# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 14:38:56 2022

@author: dows
"""

"""
Created on Sat Feb 26 22:55:44 2022

@author: dows
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time
import numpy as np
import math
from copy import deepcopy
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)



class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}
        
        #akt additions
        self.cols = ['reqID','ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
        self.df = pd.DataFrame(columns=self.cols)
        self.symbollst=[]
        
        
    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        else:
            self.data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"low":bar.low,"Close":bar.close,"Volume":bar.volume})
        
        #print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId,bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume))
    
        #akt additions
        ticker=self.symbollst[reqId]
        self.df.loc[len(self.df)] = [reqId,ticker, bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume]

def usTechStk(symbol,sec_type="STK",currency="USD",exchange="SMART"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract

def histData(app,req_num,contract,duration,candle_size):
    """extracts historical data"""
    
    app.reqHistoricalData(reqId=req_num,
                          contract=contract,
                          endDateTime='',
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='ADJUSTED_LAST',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=0,
                          chartOptions=[]) # EClient function to request contract details

def websocket_con():
    app.run()

###################storing trade app object in dataframe#######################
def setDataframeindex(df):
    "returns extracted historical data in dataframe format"
    df.set_index("date",inplace=True)
    df.index = pd.to_datetime(df.index)
    #df.index = pd.to_datetime(df.index,unit='ms')
    #read up to change date index from object to date
    return df
################################################################################

def volatile(DF):
    df = DF.copy()
    Alength=0
    effectiveLen=math.ceil((Alength+1)/2)
    df['Volatile']=df['high']+df['low']+df['Close']+df['Open']
    df['Volatile']=np.tan(df['Volatile'].astype(float))
    df['Volatile']=df['Volatile'].round(2)
    return df['Volatile']

def ranges(DF):
    df = DF.copy()
    df['Range']=(df['high']-df['low'])*100/df['low']
    return df['Range']

def stochOscltr(DF,a=20,b=3):
    """function to calculate Stochastics
       a = lookback period
       b = moving average window for %D"""
    df = DF.copy()
    df['C-L'] = df['close'] - df['low'].rolling(a).min()
    df['H-L'] = df['high'].rolling(a).max() - df['low'].rolling(a).min()
    df['%K'] = df['C-L']/df['H-L']*100
    #df['%D'] = df['%K'].ewm(span=b,min_periods=b).mean()
    return df['%K'].rolling(b).mean()

def midpoint(DF):
    df = DF.copy()
    df['Midpoint'] = (df['High']+df['low'])/2
    
    return df['Midpoint']

def rollmax(DF):
    df = DF.copy()
    df['RollMax'] = df['High'].rolling(780, min_periods=1).max().shift(1)
    df['RollMax'] = df['RollMax'].replace(np.nan, 0)
    return df['RollMax']

def rollmin(DF):
    df = DF.copy()
    df['RollMin'] = df['low'].rolling(780, min_periods=1).min().shift(1)
    df['RollMin'] = df['RollMin'].replace(np.nan, 0)
    return df['RollMin']
def buy(DF):
    df = DF.copy()
    df['Buy']=(df['low']<=(0.88*df['RollMax']))
    return df['Buy']

def sell(DF):
    df = DF.copy()
    df['Sell']=(df['High']>=(1.08*df['RollMin']))
    return df['Sell']
#def symbol(DF):
   # df = DF.copy()
   # df['Symbol']=ticker
    #return df['Symbol']


#def trade(DF):
#    df = DF.copy()
 #   if df['Close']<=(1.009*df['RollMin']):
#       return 'buy'
#    elif (df['Close']>=(1.07*df['RollMin'])):
 #        return 'sell'
#    elif(df['Close']>=(0.93*df['RollMax'])):   
 #         return 'sell'
 #   else :
#     return 'NA'

#def multitick_df_get(ticker):
#    multi_df=[]
#    for ticker in tickers:
    #Vols=[]
    #PosVolat=[]
    #NegaVolat=[]
    #
        #print("Calculating volume extraction ",ticker)
 #       singleVol=singleVols(ticker)
 #       if not singleVols.empty:
 #           multi_df.append(singleVol)
#    all_df=pd.concat(multi_df)
#    return print(all_df)
    

    #PosVolat=pd.concat(lf[ticker].loc[(lf[ticker]["Volatile"] >= 100)])
    #NegaVolat=pd.concat(lf[ticker].loc[(lf[ticker]["Volatile"] <=-100)])

#def Select(DF):
   # lf=DF.copy()
   # df_new_tier01_view = lf.loc[( lf['volatile']>=100) ]
   # df_new_tier01 = df_new_tier01_view.copy()
   # final1 = df_new_tier01.loc[:, ['Ticker','Close','low','volatile']]
   # return print(final1)


def getdf(app):  
    app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
    con_thread = threading.Thread(target=websocket_con, daemon=True)
    con_thread.start()
    time.sleep(1) # some latency added to ensure that the connection is established
    
    #########TIME SCENARIO#####################  
    tickers = ['dwac','sxtc']
    app.symbollst=tickers
    for ticker in tickers:
        histData(app,tickers.index(ticker),usTechStk(ticker),'1 W', '3 mins')
        time.sleep(5)
        #S,D,W,M,Y#1,5,10,15,30S,1,2,33,5,10,15,20,30mins

    df = app.df
    #need to set index and set it as datetimeobject
    #df=setDataframeindex(df)
    tickers_captured = df['ticker'].unique().tolist()
    print("*" * 50 )
    print(df.info())
    print(f'tickers captured: {tickers_captured}')
    print(df.head(5))
    print(df.tail(5))
    print("*" * 50 )
    return df

 ###############################TECHNICALS########################################

def addIndicators(df):
      #print("Calculating MACD & Stochastics for ",s)
      df["stoch"] = stochOscltr(df)
      #df["Volatile"] = volatile(df)
      #df["Range"] = ranges(df)
      #df["RollMax"] = rollmax(df)
      #df["RollMin"] = rollmin(df)
      #df["RollMin"] = rollmin(df)
      #df["midpoint"]= midpoint(df)
      #df["Buy"] = buy(df)
      #df["Sell"] = sell(df)
      #df.dropna(inplace=True)
      #vols=[df.loc[(df["Volume"] >= 100)]]
      return df


def savedfasXlsx(df):
    #not done yet
    pass


def main():
    app = TradeApp()
    df=getdf(app)
    #df=addIndicators(df)
    savedfasXlsx(df)
  