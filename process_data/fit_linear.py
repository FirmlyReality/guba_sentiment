import statsmodels.tsa.stattools as tsa
import numpy as np
import statsmodels.api as sm
import tushare as ts
import pandas as pd
import math

BSI_file = "HS300_MsgBSI.csv"
Fama_French_File = "STK_MKT_ThrfacDay.csv"

def fit_linear(y,*X):
    Xs = []
    for x in X:
        assert len(x) == len(y)
        Xs.append(np.array(x))
    #print(Xs)
    x = np.array(Xs).T
    #print(x)
    y = np.array(y)
    X = sm.add_constant(np.array(x))
    mod = sm.OLS(y,X)
    res = mod.fit()
    print(res.summary())

def fit_predict(y,*X):
    Xs = []
    for x in X:
        assert len(x) == len(y)
        Xs.append(np.array(x))
    #print(Xs)
    x = np.array(Xs).T
    #print(x)
    y = np.array(y)
    X = sm.add_constant(np.array(x))
    mod = sm.OLS(y[:700],X[:700])
    res = mod.fit()
    print(res.summary())
    y_pred = res.predict(X[700:])
    y_true = y[700:]
    y_dis = y_true-y_pred
    err = np.sum(y_dis*y_dis)
    print(err)
 
if __name__ == "__main__":

    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    print(stocks300)
        
    data = pd.read_csv(BSI_file)
    data.index = data['date']
    preMsgBSIs = data['preMsgBSI']
    intMsgBSIs = data['intMsgBSI']
    aftMsgBSIs = data['aftMsgBSI']
    preallMsgBSIs = data['preallMsgBSI']
    aftallMsgBSIs = data['aftallMsgBSI']
    preallArgS = data['preallArgS']
    intArgS = data['intArgS']
    
    stock_open = list(stocks300.open)
    stock_close = list(stocks300.close)
    volume = list(stocks300.volume)
        
    close_returns = []
    for i in range(1,len(stock_close)):
        close_returns.append(stock_close[i] / stock_close[i-1] - 1)
        
    open_returns = []
    for i in range(1,len(stock_open)):
        open_returns.append(stock_open[i] / stock_close[i-1] - 1)
            
    today_returns = []
    for i in range(len(stock_open)):
        today_returns.append(stock_close[i] / stock_open[i] - 1)
    
    lnvolume = []    
    for v in volume:
        lnvolume.append(math.log(v))
        
    Rft_list = [["2014-11-22",2.35], ["2015-03-01",2.10], ["2015-05-11",1.85], ["2015-06-28",1.60], ["2015-08-26",1.35], ["2015-10-24",1.10]]
    Rft = []
    last_i = -1
    for date in stocks300.date:
        if last_i < len(Rft_list)-1 and date >= Rft_list[last_i+1][0]:
            last_i += 1
        Rft.append(Rft_list[last_i][1]/100)
    #print(Rft)
    
    stock_data = pd.DataFrame()
    stock_data['HS300_date'] = stocks300.date
    stock_data['close_price'] = stocks300.close
    stock_data['close_returns'] = [0]+close_returns
    stock_data['open_returns'] = [0]+open_returns
    stock_data['today_returns'] = today_returns
    stock_data['volume'] = volume
    stock_data['Rft'] = Rft
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
    print(tsa.adfuller(volume,1))
   
    print("ADF test for ln(volume):")
    print(tsa.adfuller(lnvolume,1))
    
    print("ADF test for preallArgS:")
    print(tsa.adfuller(preallArgS))
               
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

    print("Fit lnvolume-preallArgS:")
    fit_linear(lnvolume,preallArgS)   

    print("Fit lnvolume-intArgS:")
    fit_linear(lnvolume,intArgS)      
    
    frac_data = pd.read_csv(Fama_French_File,sep='\t')
    #print(frac_data)
    frac_data = frac_data[frac_data['MarkettypeID'] == 'P9709'].sort_values(by='TradingDate')
    frac_data.index = frac_data['TradingDate']
    RMRf = frac_data['RiskPremium1'][1:]
    SMB = frac_data['SMB1'][1:]
    HML = frac_data['HML1'][1:]
    new_returns = [close_returns[i] - Rft[i+1] for i in range(len(close_returns))]
    #print(len(RMRf))
    #print(len(new_returns))
    #print(np.array(close_returns))
    #print(np.array(Rft))
    #print(np.array(new_returns))
    fit_linear(new_returns[:-1],RMRf[:-1],SMB[:-1],HML[:-1],new_returns[1:])
    #fit_linear(new_returns,preallMsgBSIs[1:])
    fit_linear(new_returns,RMRf,SMB,HML,preallMsgBSIs[1:])
    
    tmpBSI2 = []
    tmpBSI1 = []
    tmpBSI0 = []
    newpreall = []
    std = 0#np.average(preallMsgBSIs[1:]) + np.var(preallMsgBSIs[1:])
    print(std)
    for b in preallMsgBSIs[1:]:
        b2 = 0
        b1 = 0
        b0 = 0
        if b >= std:
            b2 = b
        elif b <= -std:
            b0 = b
        else:
            b1 = b
        if b > 3*std:
            newpreall.append(np.average(preallMsgBSIs[1:]))
        elif b < -3*std:
            newpreall.append(np.average(preallMsgBSIs[1:]))
        else:
            newpreall.append(b)
        tmpBSI0.append(b0)
        tmpBSI1.append(b1)
        tmpBSI2.append(b2)
    fit_linear(close_returns,RMRf,SMB,HML,newpreall)
    fit_linear(close_returns,RMRf,SMB,HML,tmpBSI2,tmpBSI1,tmpBSI0)
    fit_linear(close_returns,tmpBSI2,tmpBSI0)
    
    fit_predict(new_returns,RMRf,SMB,HML)
    fit_linear(new_returns,RMRf,preallMsgBSIs[1:])
    fit_linear(close_returns[1:],close_returns[:-1],preallMsgBSIs[2:])
    
    stock_data = ts.get_k_data(code="000063", start='2015-01-01', end='2018-10-01') 
    stock_date = stock_data.date
    stock_close = list(stock_data.close)    
    RMRf = frac_data['RiskPremium1'].loc[stock_date[1:]]
    SMB = frac_data['SMB1'].loc[stock_date[1:]]
    HML = frac_data['HML1'].loc[stock_date[1:]]
    
    close_returns = []
    for i in range(1,len(stock_close)):
        close_returns.append(stock_close[i] / stock_close[i-1] - 1)
    preMsgBSI = list(data['preMsgBSI'].loc[stock_date])
    preallMsgBSI = list(data['preallMsgBSI'].loc[stock_date])
    intMsgBSI = list(data['intMsgBSI'].loc[stock_date])
        
    fit_linear(close_returns,RMRf,SMB,HML)
    fit_linear(close_returns,RMRf,SMB,HML,preMsgBSI[1:])
    fit_linear(close_returns,RMRf,SMB,HML,preallMsgBSI[1:])
    fit_linear(close_returns,RMRf,SMB,HML,intMsgBSI[1:])