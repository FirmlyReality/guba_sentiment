import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
import statsmodels.api as sm
import math, sys
import statsmodels.tsa.stattools as tsa
from datetime import datetime, timedelta

#need_stocks = ['000002']
#sumres_dir = "../../../data/sum_results"
tiezi_weight = 0.8
reply_weight = 1 - tiezi_weight

def compute_MsgBSI(tcnt, rcnt, tsum, rsum):
    '''print("tcnt: %s"%str(tcnt))
    print("rcnt: %s"%str(rcnt))
    print("tsum: %s"%str(tsum))
    print("rsum: %s"%str(rsum))'''
    fenmu = sum(tsum[1:])*tiezi_weight + sum(rsum[1:])*reply_weight
    if fenmu == 0:
        return 0
    else:
        BSI = ((tsum[3] - tsum[1])*tiezi_weight + (rsum[3]-rsum[1])*reply_weight) / fenmu
        MsgBSI = BSI * math.log(sum(tcnt[1:]) + sum(rcnt[1:]) +1) 
        #print("MsgBSI: %s"%str(MsgBSI))
        return MsgBSI
        
def fit_linear(y,x):
    assert len(x) == len(y)
    x = np.array(x)
    y = np.array(y)
    X = sm.add_constant(np.array(x))
    mod = sm.OLS(y,X)
    res = mod.fit()
    print(res.summary())    
    
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("python get_gegu_MsgBSI.py <inputDir> <outputDir>")
        exit(1)
    
    inputDir = sys.argv[1]
    outputDir = sys.argv[2]

    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    stocks_date = ['2015-01-01'] + list(stocks300.date)
    print(stocks_date)
    exit(0)
    
    print("Read from inputDir %s" % inputDir)
    files = os.listdir(inputDir)
    files = sorted(files)
    
    for file in files:
        print("Process file: %s"%file)
        #fig = plt.figure()
        #ax1 = fig.add_subplot(111)
        #plt.plot(datesl,indicators_pre,'b',alpha=0.9)
        #plt.plot(datesl,indicators_int,alpha=0.9)
        sum_data = pd.read_csv(file)
        sum_data.index = sum_data['date']
        #print(sum_data)
        
        aftMsgBSI = []
        intMsgBSI = []
        allMsgBSI = []
        for i in range(1,len(stocks_date)):
            now_date = datetime.strptime(stocks_date[i],"%Y-%m-%d")
            last_date = datetime.strptime(stocks_date[i-1],"%Y-%m-%d")
            
            aft_t_cnt = np.zeros(4)
            aft_r_cnt = np.zeros(4)
            aft_t_sum = np.zeros(4)
            aft_r_sum = np.zeros(4)
            int_t_cnt = np.zeros(4)
            int_r_cnt = np.zeros(4)
            int_t_sum = np.zeros(4)
            int_r_sum = np.zeros(4)            
            all_t_cnt = np.zeros(4)
            all_r_cnt = np.zeros(4)
            all_t_sum = np.zeros(4)
            all_r_sum = np.zeros(4)
            
            date = now_date
            Beta = 0.8
            beta_now = 1
            while date > last_date:
                d = sum_data.loc[date]
                #print("Compute PreMsgBSI...")
                aft_t_cnt += beta_now * np.array([d['aft_t_'+str(i)+'_cnt'] for i in range(4)])
                aft_r_cnt += beta_now * np.array([d['aft_r_'+str(i)+'_cnt'] for i in range(4)])
                aft_t_sum += beta_now * np.array([d['aft_t_'+str(i)+'_prob'] for i in range(4)])
                aft_r_sum += beta_now * np.array([d['aft_r_'+str(i)+'_prob'] for i in range(4)])
                
                #print("Compute IntMsgBSI...")
                int_t_cnt += beta_now * np.array([d['int_t_'+str(i)+'_cnt'] for i in range(4)])
                int_r_cnt += beta_now * np.array([d['int_r_'+str(i)+'_cnt'] for i in range(4)])
                int_t_sum += beta_now * np.array([d['int_t_'+str(i)+'_prob'] for i in range(4)])
                int_r_sum += beta_now * np.array([d['int_r_'+str(i)+'_prob'] for i in range(4)])
                
                #print("Compute AllMsgBSI...")
                all_t_cnt += beta_now * (aft_t_cnt + int_t_cnt)
                all_r_cnt += beta_now * (aft_r_cnt + int_r_cnt)
                all_t_sum += beta_now * (aft_t_sum + int_t_sum)
                all_r_sum += beta_now * (aft_r_sum + int_r_sum)
                
                date -= timedelta(days=1)
                beta_now *= Beta
                
            aftMsgBSI.append(compute_MsgBSI(aft_t_cnt, aft_r_cnt, aft_t_sum, aft_r_sum))
            intMsgBSI.append(compute_MsgBSI(int_t_cnt, int_r_cnt, int_t_sum, int_r_sum))
            allMsgBSI.append(compute_MsgBSI(all_t_cnt, all_r_cnt, all_t_sum, all_r_sum))
        preMsgBSI = aftMsgBSI[:-1]

        stock_data = ts.get_k_data(code=code, start='2015-01-01', end='2018-10-01')
        print(stock_data)
        stock_date = list(stock_data.date)
        
        stock_open = list(stock_data.open)
        stock_close = list(stock_data.close)
        
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
        print(tsa.adfuller(close_returns))
        
        print("ADF test for today_returns:")
        print(tsa.adfuller(today_returns))
        
        print("ADF test for open_returns:")
        print(tsa.adfuller(open_returns))
        
        print("ADF test for preMsgBSI:")
        print(tsa.adfuller(preMsgBSI))
        
        print("ADF test for intMsgBSI:")
        print(tsa.adfuller(intMsgBSI))
        
        print("ADF test for allMsgBSI:")
        print(tsa.adfuller(allMsgBSI))
        
        print("ADF test for aftMsgBSI:")
        print(tsa.adfuller(aftMsgBSI))
                  
        #stock_returns = np.array(stock_returns)*100
        #plt.plot(stock_date,stock_returns,'r',alpha=0.9)

        print("Fit today_returns-preMsgBSI:")
        fit_linear(today_returns[1:],preMsgBSI)
        
        print("Fit today_returns-intMsgBSI:")
        fit_linear(today_returns,intMsgBSI)
        
        print("Fit today_returns-allMsgBSI[-1]:")
        fit_linear(today_returns[1:],allMsgBSI[:-1])

        print("Fit today_returns-aftMsgBSI:")
        fit_linear(today_returns,aftMsgBSI)
        
        print("Fit open_returns-preMsgBSI:")
        fit_linear(open_returns,preMsgBSI)       
        
        print("Fit open_returns-allMsgBSI[-1]:")
        fit_linear(open_returns,allMsgBSI[:-1])
        
        print("Fit close_returns-allMsgBSI:")
        fit_linear(close_returns,allMsgBSI[:-1])
        
        print("Fit close_returns-preMsgBSI:")
        fit_linear(close_returns,preMsgBSI)
        
        print("Fit close_returns-intMsgBSI[-1]:")
        fit_linear(close_returns,intMsgBSI[:-1])
        
        print("Fit close_returns-intMsgBSI:")
        fit_linear(close_returns,intMsgBSI[1:])
        
        print("Fit close_returns-aftMsgBSI:")
        fit_linear(close_returns,aftMsgBSI[1:])