from linearmodels.asset_pricing import LinearFactorModel
from linearmodels.asset_pricing import LinearFactorModelGMM
import pandas as pd
import numpy as np
import statsmodels.api as sm
import math
import matplotlib.pyplot as plt
import tushare as ts

inputdir = "../res_data1"
startsamples = 0

def gentbsi(sBSI,gBSI):
    sBSI = np.array(sBSI)
    gBSI = np.array(gBSI)
    return 0.8*sBSI+0.2*gBSI

def normaliza(ndata):
    ndata = np.array(ndata)
    stderr = np.std(ndata)
    ave = np.mean(ndata)
    return (ndata-ave) / stderr
    
def fit_linear(y,X):
    y = np.array(y)
    X = sm.add_constant(X)
    mod = sm.OLS(y,X)
    res = mod.fit()
    return res

def twoStep(st_ret,X):
    time_res = []
    for col in st_ret.columns:
        print(len(st_ret[col]))
        print(len(X))
        time_res.append(fit_linear(st_ret[col],X))
        print(time_res[-1].summary())
        
    res_params = []
    for res in time_res:
        res_params.append(res.params[1:])
    res_params = np.array(res_params)
    x_params = sm.add_constant(res_params)

    rets = np.array(st_ret.mean())
    cov = st_ret.cov()
    print(rets)
    input()
    res = sm.GLS(rets,x_params).fit()
    print(res.summary())
    
def FamaMacBeth(st_ret,X):
    time_res = []
    for col in st_ret.columns:
        print(len(st_ret[col]))
        print(len(X))
        time_res.append(fit_linear(st_ret[col],X))
        print(time_res[-1].summary())
        #input()
    #res = fit_linear(st_ret,X)
    #print(res.summary())
    #print(res.param)
    res_params = []
    for res in time_res:
        res_params.append(res.params[1:])
    res_params = np.array(res_params)
    x_params = sm.add_constant(res_params)
    print(res_params)
    #input()
    
    cross_sec_params = []
    cov = st_ret.cov()
    print(cov)
    
    print(st_ret)
    for t in st_ret.index:
        d = np.array(st_ret.loc[t])
        '''fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.scatter(list(res_params.T[0]),list(d))
        print(d)
        print(res_params.T[0])
        print(res_params)
        fig.show()
        input()'''
        res = sm.GLS(d,x_params,sigma=cov).fit()
        cross_sec_params.append(res.params)
        print(res.summary())
        #input()
    
    cs_params = []
    for i in range(len(cross_sec_params[1])):
        cs_params.append([csp[i] for csp in cross_sec_params])
    #print(cs_params)
    cs_params = np.array(cs_params)
    print(cs_params)
    for i in range(len(cs_params)):
        #print(cs_params[i])
        m = np.mean(cs_params[i])
        std = np.std(cs_params[i],ddof=1)
        print(np.mean(cs_params[i]))
        print(std)
        print(m/(std/math.sqrt(len(X))))
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.scatter(range(len(cs_params[i])),list(cs_params[i]))
        fig.show()
        input()
        
def out_groups(nums):
    m = np.mean(nums)
    std = np.std(nums,ddof=1)
    h = m+3*std
    l = m-3*std
    cnt = 0
    for i in range(len(nums)):
        if nums[i] > h or nums[i] < l:
            if i == 0:
                left = 0
            else:
                left = nums[i-1]
            if i == len(nums)-1:
                right = 0
            else:
                right = nums[i+1]
             
            nums[i] = 0.5*left + 0.5*right
            cnt += 1
    print("Total out nums:%d"%cnt)
    #input()
    return nums
    
def process_ret(st_ret):
    for col in st_ret.columns:
        st_ret[col] = list(out_groups(st_ret[col]))
    
if __name__ == "__main__":

    fama_factors = pd.read_csv(inputdir+"/RESSET_mn_Fama_French.csv")
    #fama_factors = pd.read_csv(inputdir+"/2fama_factors55_60.csv")
    #ret_g = pd.read_csv(inputdir+"/2stocks_group_ret55_60.csv")
    ret_g = pd.read_csv(inputdir+"/RESSET_mn_stock_ret.csv")
    rft_data = pd.read_csv(inputdir+"/rft.csv")
    bsi_data = pd.read_csv(inputdir+"/HS300_MsgBSI.csv")
    g_bsi = pd.read_csv(inputdir+"/g_MsgBSI.csv")
    hs300_return = pd.read_csv(inputdir+"/HS300_returns.csv")
     
    groupret = ret_g.groupby(by=['Sizeflg','BMflg'])
    print(groupret.mean())
    portfolios = pd.DataFrame()
    for gname, gdata in groupret:
        print(gname)
        portfolios[str(gname)] = list(gdata['Pmonret_tmv'])
        #print(gdata)
    print(portfolios)
    
    '''cn800 = ts.get_k_data('000906', index=True,start="2015-01-01",end="2018-10-01")
    print(cn800.close)
    cn800_return = np.array(cn800.close[1:]) / np.array(cn800.close[:-1]) - 1
    print(cn800_return)'''
    #input()
    
    factors = fama_factors[['Rmrf_tmv','Smb_tmv','Hml_tmv']]
    #factors = fama_factors[['RiskPremium1','SMB1','HML1']]
    #factors = fama_factors[['MktRet','SMB','HML']]
    #factors['HML'] = -fama_factors['HML']
    #factors['BSI'] = bsi_data['intMsgBSI']
    #print(factors['MktRet'])
    #factors['MktRet'] = factors['MktRet'] - rft_data['rft_country1']
    #print(factors.mean())
    #factors = cn800_return - np.array(rft_data['rft_country1'][1:])
    print(factors)
    #input()
    #exit(0)
    #key_col = list(ret_g.columns)
    #key_col.remove('date')
    #portfolios = ret_g[key_col]
    #print(portfolios)
    #print(ret_g)
    #factors = factors[startsamples:]
    #portfolios = portfolios[startsamples:]
    
    #for col in portfolios.columns:
        #portfolios[col] = portfolios[col] - rft_data['rft_country1']
    
    #print(ret_g)
    #factors['BSI'] = list(bsi_data['preMsgBSI'])[300:]
    print(factors)
    #process_ret(portfolios)
    #process_ret(factors)
    
    #FamaMacBeth(portfolios,factors)
    twoStep(portfolios,factors)