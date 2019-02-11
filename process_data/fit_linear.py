import statsmodels.tsa.stattools as tsa
import numpy as np
import statsmodels.api as sm
import tushare as ts
import pandas as pd
import math

BSI_file = "HS300_MsgBSI.csv"

def fit_linear(y,x):
    assert len(x) == len(y)
    x = np.array(x)
    y = np.array(y)
    X = sm.add_constant(np.array(x))
    mod = sm.OLS(y,X)
    res = mod.fit()
    print(res.summary()) 
    
if __name__ == "__main__":

    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    print(stocks300)
    
    data = pd.read_csv(BSI_file)
    preMsgBSIs = data['preMsgBSI']
    intMsgBSIs = data['intMsgBSI']
    aftMsgBSIs = data['aftMsgBSI']
    preallMsgBSIs = data['preallMsgBSI']
    aftallMsgBSIs = data['aftallMsgBSI']  
    
    stock_open = list(stocks300.open)
    stock_close = list(stocks300.close)
    volume = list(stocks300.volume)
        
    close_returns = []
    for i in range(1,len(stock_close)):
        close_returns.append(math.log(stock_close[i] / stock_close[i-1]))
        
    open_returns = []
    for i in range(1,len(stock_open)):
        open_returns.append(math.log(stock_open[i] / stock_close[i-1]))
            
    today_returns = []
    for i in range(len(stock_open)):
        today_returns.append(math.log(stock_close[i] / stock_open[i]))
    
    volumes = []    
    for v in volume:
        volumes.append(math.log(v))
    
    stock_data = pd.DataFrame()
    stock_data['close_returns'] = [0]+close_returns
    stock_data['open_returns'] = [0]+open_returns
    stock_data['today_returns'] = today_returns
    stock_data['volume'] = volume
    stock_data.to_csv("HS300_returns.csv",index=False)
        
    print("ADF test for close_returns:")
    print(tsa.adfuller(close_returns,1))
        
    print("ADF test for today_returns:")
    print(tsa.adfuller(today_returns,1))
        
    print("ADF test for open_returns:")
    print(tsa.adfuller(open_returns,1))
        
    print("ADF test for preMsgBSI:")
    print(tsa.adfuller(preMsgBSIs,1))
        
    print("ADF test for intMsgBSI:")
    print(tsa.adfuller(intMsgBSIs,1))

    print("ADF test for aftMsgBSI:")
    print(tsa.adfuller(aftMsgBSIs,1))
        
    print("ADF test for preallMsgBSI:")
    print(tsa.adfuller(preallMsgBSIs,1))
        
    print("ADF test for aftallMsgBSI:")
    print(tsa.adfuller(aftallMsgBSIs,1))
    
    print("ADF test for volume:")
    print(tsa.adfuller(volume))
   
    print("ADF test for ln(volume):")
    print(tsa.adfuller(volumes))
               
        #stock_returns = np.array(stock_returns)*100
        
    print(len(preMsgBSIs))
    print(len(today_returns))

    print("Fit today_returns-preMsgBSI:")
    fit_linear(today_returns,preMsgBSIs)
        
    print("Fit today_returns-intMsgBSI:")
    fit_linear(today_returns,intMsgBSIs)
        
    #print("Fit today_returns-allMsgBSI[-1]:")
    #fit_linear(today_returns[1:],allMsgBSI[:-1])

    print("Fit today_returns-aftMsgBSI:")
    fit_linear(today_returns,aftMsgBSIs)
        
    print("Fit open_returns-preMsgBSI:")
    fit_linear(open_returns,preMsgBSIs[1:])       
        
    print("Fit open_returns-intMsgBSI[-1]:")
    fit_linear(open_returns,intMsgBSIs[:-1])
        
    print("Fit close_returns-preallMsgBSI:")
    fit_linear(close_returns,preallMsgBSIs[1:])
        
    print("Fit close_returns-preMsgBSI:")
    fit_linear(close_returns,preMsgBSIs[1:])
        
    print("Fit close_returns-intMsgBSI[-1]:")
    fit_linear(close_returns,intMsgBSIs[:-1])
        
    print("Fit close_returns-intMsgBSI:")
    fit_linear(close_returns,intMsgBSIs[1:])
        
    print("Fit close_returns-aftMsgBSI:")
    fit_linear(close_returns,aftMsgBSIs[1:])

    print("Fit volume-ArgS:")
    fit_linear(close_returns,aftMsgBSIs[1:])     