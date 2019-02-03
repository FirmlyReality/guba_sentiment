import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
import statsmodels.api as sm
import math
import statsmodels.tsa.stattools as tsa

need_stocks = ['000413']
sumres_dir = "../../../data/sum_results"

def compute_MsgBSI(tcnt, rcnt, tsum, rsum):
    '''print("tcnt: %s"%str(tcnt))
    print("rcnt: %s"%str(rcnt))
    print("tsum: %s"%str(tsum))
    print("rsum: %s"%str(rsum))'''
    fenmu = sum(tsum[1:])+sum(rsum[1:])
    if fenmu == 0:
        return 0
    else:
        BSI = (tsum[3]+rsum[3] - tsum[1]-rsum[1]) / fenmu
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
    for code in need_stocks:
        print("Process stocks code:%s"%code)
        #fig = plt.figure()
        #ax1 = fig.add_subplot(111)
        #plt.plot(datesl,indicators_pre,'b',alpha=0.9)
        #plt.plot(datesl,indicators_int,alpha=0.9)
        sum_data = pd.read_csv(sumres_dir+"/"+code+".csv")
        sum_data.index = sum_data['date']
        #print(sum_data)
        
        stock_data = ts.get_k_data(code=code, start='2015-01-01', end='2018-10-01')
        print(stock_data)
        stock_date = list(stock_data.date)
        
        aftMsgBSI = []
        intMsgBSI = []
        allMsgBSI = []
        for date in stock_date:
            d = sum_data.loc[date]
            #print("Compute PreMsgBSI...")
            aft_t_cnt = [d['aft_t_'+str(i)+'_cnt'] for i in range(4)]
            aft_r_cnt = [d['aft_r_'+str(i)+'_cnt'] for i in range(4)]
            aft_t_sum = [d['aft_t_'+str(i)+'_prob'] for i in range(4)]
            aft_r_sum = [d['aft_r_'+str(i)+'_prob'] for i in range(4)]
            aftMsgBSI.append(compute_MsgBSI(aft_t_cnt, aft_r_cnt, aft_t_sum, aft_r_sum))
            
            #print("Compute IntMsgBSI...")
            int_t_cnt = [d['int_t_'+str(i)+'_cnt'] for i in range(4)]
            int_r_cnt = [d['int_r_'+str(i)+'_cnt'] for i in range(4)]
            int_t_sum = [d['int_t_'+str(i)+'_prob'] for i in range(4)]
            int_r_sum = [d['int_r_'+str(i)+'_prob'] for i in range(4)]
            intMsgBSI.append(compute_MsgBSI(int_t_cnt, int_r_cnt, int_t_sum, int_r_sum))
            
            #print("Compute AllMsgBSI...")
            all_t_cnt = [aft_t_cnt[i]+int_t_cnt[i] for i in range(4)]
            all_r_cnt = [aft_r_cnt[i]+int_r_cnt[i] for i in range(4)]
            all_t_sum = [aft_t_sum[i]+int_t_sum[i] for i in range(4)]
            all_r_sum = [aft_r_sum[i]+int_r_sum[i] for i in range(4)]
            allMsgBSI.append(compute_MsgBSI(all_t_cnt, all_r_cnt, all_t_sum, all_r_sum))
        preMsgBSI = aftMsgBSI[:-1]
                   
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