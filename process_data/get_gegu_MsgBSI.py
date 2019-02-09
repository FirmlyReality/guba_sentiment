import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
import statsmodels.api as sm
import math, sys, os
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
    #date_300 = ['2015-01-01'] + list(stocks300.date)
    #print(date_300)
    #exit(0)
    
    print("Read from inputDir %s" % inputDir)
    files = os.listdir(inputDir)
    files = sorted(files)
    
    for file in files[453:]:
        code = file.split(".")[0]
        print("Process file: %s, stock_code:%s "%(file, code))
        
        stock_data = ts.get_k_data(code=code, start='2015-01-01', end='2018-10-01')
        #print(stock_data)
        if len(stock_data) == 0:
            print("Code %s does not exist!!!" % code)
            stock_data = stocks300
        stock_date = ['2015-01-01'] + list(stock_data.date)
        #print(stock_date)
        #fig = plt.figure()
        #ax1 = fig.add_subplot(111)
        #plt.plot(datesl,indicators_pre,'b',alpha=0.9)
        #plt.plot(datesl,indicators_int,alpha=0.9)
        sum_data = pd.read_csv(os.path.join(inputDir,file))
        sum_data.index = sum_data['date']
        #print(sum_data)
        
        aftMsgBSI = []
        intMsgBSI = []
        aftallMsgBSI = []
        preMsgBSI = []
        preallMsgBSI = []
        for i in range(1,len(stock_date)):
            now_date = datetime.strptime(stock_date[i],"%Y-%m-%d")
            last_date = datetime.strptime(stock_date[i-1],"%Y-%m-%d")
            
            date_str = now_date.strftime("%Y-%m-%d")
            d = sum_data.loc[date_str]
            aft_t_cnt = np.array([d['aft_t_'+str(i)+'_cnt'] for i in range(4)])
            aft_r_cnt = np.array([d['aft_r_'+str(i)+'_cnt'] for i in range(4)])
            aft_t_sum = np.array([d['aft_t_'+str(i)+'_prob'] for i in range(4)])
            aft_r_sum = np.array([d['aft_r_'+str(i)+'_prob'] for i in range(4)])
            
            int_t_cnt = np.array([d['int_t_'+str(i)+'_cnt'] for i in range(4)])
            int_r_cnt = np.array([d['int_r_'+str(i)+'_cnt'] for i in range(4)])
            int_t_sum = np.array([d['int_t_'+str(i)+'_prob'] for i in range(4)])
            int_r_sum = np.array([d['int_r_'+str(i)+'_prob'] for i in range(4)])
            
            aftall_t_cnt = (aft_t_cnt + int_t_cnt)
            aftall_r_cnt = (aft_r_cnt + int_r_cnt)
            aftall_t_sum = (aft_t_sum + int_t_sum)
            aftall_r_sum = (aft_r_sum + int_r_sum)            
            
            pre_t_cnt = np.zeros(4)
            pre_r_cnt = np.zeros(4)
            pre_t_sum = np.zeros(4)
            pre_r_sum = np.zeros(4)
            
            date = now_date
            Beta = 0.6
            beta_now = 1
            while date > last_date:
                date -= timedelta(days=1)
                date_str = date.strftime("%Y-%m-%d")
                d = sum_data.loc[date_str]
                pre_t_cnt += beta_now * np.array([d['aft_t_'+str(i)+'_cnt'] for i in range(4)])
                pre_r_cnt += beta_now * np.array([d['aft_r_'+str(i)+'_cnt'] for i in range(4)])
                pre_t_sum += beta_now * np.array([d['aft_t_'+str(i)+'_prob'] for i in range(4)])
                pre_r_sum += beta_now * np.array([d['aft_r_'+str(i)+'_prob'] for i in range(4)])
                
                if date == last_date:
                    preMsgBSI.append(compute_MsgBSI(pre_t_cnt, pre_r_cnt, pre_t_sum, pre_r_sum))
                pre_t_cnt += beta_now * np.array([d['int_t_'+str(i)+'_cnt'] for i in range(4)])
                pre_r_cnt += beta_now * np.array([d['int_r_'+str(i)+'_cnt'] for i in range(4)])
                pre_t_sum += beta_now * np.array([d['int_t_'+str(i)+'_prob'] for i in range(4)])
                pre_r_sum += beta_now * np.array([d['int_r_'+str(i)+'_prob'] for i in range(4)])
                           
                beta_now *= Beta
                
            aftMsgBSI.append(compute_MsgBSI(aft_t_cnt, aft_r_cnt, aft_t_sum, aft_r_sum))
            intMsgBSI.append(compute_MsgBSI(int_t_cnt, int_r_cnt, int_t_sum, int_r_sum))
            aftallMsgBSI.append(compute_MsgBSI(aftall_t_cnt, aftall_r_cnt, aftall_t_sum, aftall_r_sum))          
            preallMsgBSI.append(compute_MsgBSI(pre_t_cnt, pre_r_cnt, pre_t_sum, pre_r_sum))
            
        MsgBSI_data = pd.DataFrame()
        MsgBSI_data['date'] = stock_date[1:]
        MsgBSI_data['preMsgBSI'] = preMsgBSI
        MsgBSI_data['intMsgBSI'] = intMsgBSI
        MsgBSI_data['aftMsgBSI'] = aftMsgBSI
        MsgBSI_data['preallMsgBSI'] = preallMsgBSI
        MsgBSI_data['aftallMsgBSI'] = aftallMsgBSI
        MsgBSI_data.to_csv(os.path.join(outputDir,file),index=False)
        
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

        print("ADF test for aftMsgBSI:")
        print(tsa.adfuller(aftMsgBSI))
        
        print("ADF test for preallMsgBSI:")
        print(tsa.adfuller(preallMsgBSI))
        
        print("ADF test for aftallMsgBSI:")
        print(tsa.adfuller(aftallMsgBSI))
               
        #stock_returns = np.array(stock_returns)*100
        
        print(len(preMsgBSI))
        print(len(today_returns))

        print("Fit today_returns-preMsgBSI:")
        fit_linear(today_returns,preMsgBSI)
        
        print("Fit today_returns-intMsgBSI:")
        fit_linear(today_returns,intMsgBSI)
        
        #print("Fit today_returns-allMsgBSI[-1]:")
        #fit_linear(today_returns[1:],allMsgBSI[:-1])

        print("Fit today_returns-aftMsgBSI:")
        fit_linear(today_returns,aftMsgBSI)
        
        print("Fit open_returns-preMsgBSI:")
        fit_linear(open_returns,preMsgBSI[1:])       
        
        print("Fit open_returns-intMsgBSI[-1]:")
        fit_linear(open_returns,intMsgBSI[:-1])
        
        print("Fit close_returns-preallMsgBSI:")
        fit_linear(close_returns,preallMsgBSI[1:])
        
        print("Fit close_returns-preMsgBSI:")
        fit_linear(close_returns,preMsgBSI[1:])
        
        print("Fit close_returns-intMsgBSI[-1]:")
        fit_linear(close_returns,intMsgBSI[:-1])
        
        print("Fit close_returns-intMsgBSI:")
        fit_linear(close_returns,intMsgBSI[1:])
        
        print("Fit close_returns-aftMsgBSI:")
        fit_linear(close_returns,aftMsgBSI[1:])