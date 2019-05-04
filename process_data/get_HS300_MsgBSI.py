import pandas as pd
import os
import tushare as ts
from datetime import datetime
import statsmodels.tsa.stattools as tsa
import numpy as np
import statsmodels.api as sm

BSI_dir = "../../../data/MsgBSI_data"
stocks_weight_file = "../../weights300.csv"
stocks_change_file = "../../stock_date.csv"

def fit_linear(y,x):
    assert len(x) == len(y)
    x = np.array(x)
    y = np.array(y)
    X = sm.add_constant(np.array(x))
    mod = sm.OLS(y,X)
    res = mod.fit()
    print(res.summary()) 

if __name__ == "__main__":
    
    stocks_BSI = {}
    print("Read from BSI_dir(%s) and build stocks_BSI..."%BSI_dir)
    files = os.listdir(BSI_dir)
    
    for file in files:
        code = file.split(".")[0]
        data = pd.read_csv(os.path.join(BSI_dir,file))
        data.index = data['date']
        data.drop('date',axis=1,inplace=True)
        stocks_BSI[code] = data
    
    #print(stocks_BSI)
    
    print("Read from stocks_weight_file(%s)..."%stocks_weight_file)
    weights_data = pd.read_csv(stocks_weight_file)
    weights_data.index = [s[:6] for s in weights_data['order_book_id']]
    #print(weights_data)
    
    print("Read from stocks_change_file(%s)..."%stocks_change_file)
    change_data = pd.read_csv(stocks_change_file)
    change_data = change_data[change_data['stat'] == '纳入']
    change_date = sorted(list(set(change_data['date'])))
    #print(change_date)
    
    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    date_300 = list(stocks300.date)
    #print(date_300)
    
    #print([d in date_300 for d in change_date])
    preMsgBSIs = []
    intMsgBSIs = []
    aftMsgBSIs = []
    preallMsgBSIs = []
    aftallMsgBSIs = []
    preArgS = []
    intArgS = []
    aftArgS = []
    preallArgS = []
    aftallArgS = []
    
    last_month = 0
    for date_str in date_300:
        print(date_str)
        date = datetime.strptime(date_str,"%Y-%m-%d")
        if date.month != last_month or date_str in change_date:
            print("Weights Update!!!")
            y = date.year
            m = date.month
            if date_str in change_date:
                if m == 12:
                    m = 1
                    y += 1
                else:
                    m += 1
            wdate = datetime(y,m,1).strftime("%Y%m%d")
            now_weights = weights_data[wdate].dropna()
            #print(now_weights)
        
        tmppre = 0
        tmpint = 0
        tmpaft = 0
        tmppreall = 0
        tmpaftall = 0
        argpre = 0
        argint = 0
        argaft = 0
        argpreall = 0
        argaftall = 0
        for code in now_weights.index:
            #print(code)
            #print(date_str)
            try:
                d = stocks_BSI[code].loc[date_str]               
            except Exception as err:
                print(err)
                print("Stock(%s) does not have %s data"%(code,date_str))
                d = {'preMsgBSI':0,'intMsgBSI':0,'aftMsgBSI':0,'preallMsgBSI':0,'aftallMsgBSI':0,
                    'preArgS':0,'intArgS':0,'aftArgS':0,'preallArgS':0,'aftallArgS':0}
            w = now_weights.loc[code]
            #print(w)
            tmppre += d['preMsgBSI'] * w
            tmpint += d['intMsgBSI'] * w
            tmpaft += d['aftMsgBSI'] * w
            tmppreall += d['preallMsgBSI'] * w
            tmpaftall += d['aftallMsgBSI'] * w
            argpre += d['preArgS'] * w
            argint += d['intArgS'] * w
            argaft += d['aftArgS'] * w
            argpreall += d['preallArgS'] * w
            argaftall += d['aftallArgS'] * w
        
        preMsgBSIs.append(tmppre)
        intMsgBSIs.append(tmpint)
        aftMsgBSIs.append(tmpaft)
        preallMsgBSIs.append(tmppreall)
        aftallMsgBSIs.append(tmpaftall)
        preArgS.append(argpre)
        intArgS.append(argint)
        aftArgS.append(argaft)
        preallArgS.append(argpreall)
        aftallArgS.append(argaftall)
        
        last_month = date.month
    
    res_data = pd.DataFrame()
    res_data['date'] = date_300
    res_data['preMsgBSI'] = preMsgBSIs
    res_data['intMsgBSI'] = intMsgBSIs
    res_data['aftMsgBSI'] = aftMsgBSIs
    res_data['preallMsgBSI'] = preallMsgBSIs
    res_data['aftallMsgBSI'] = aftallMsgBSIs
    res_data['preArgS'] = preArgS
    res_data['intArgS'] = intArgS
    res_data['aftArgS'] = aftArgS
    res_data['preallArgS'] = preallArgS
    res_data['aftallArgS'] = aftallArgS
    res_data.to_csv("HS300_MsgBSI.csv",index=False)
    
    '''stock_open = list(stocks300.open)
    stock_close = list(stocks300.close)
        
    close_returns = []
    for i in range(1,len(stock_close)):
        close_returns.append(stock_close[i] / stock_close[i-1] - 1)
        
    open_returns = []
    for i in range(1,len(stock_open)):
        open_returns.append(stock_open[i] / stock_close[i-1] - 1)
            
    today_returns = []
    for i in range(len(stock_open)):
        today_returns.append(stock_close[i] / stock_open[i] - 1)
        
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
    fit_linear(close_returns,aftMsgBSIs[1:])'''
    
    