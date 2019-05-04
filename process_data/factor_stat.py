from linearmodels.asset_pricing import LinearFactorModel
from linearmodels.asset_pricing import LinearFactorModelGMM
import pandas as pd
import numpy as np
import statsmodels.api as sm

inputdir = "../res_data1"
start_samples = 300
ret_file = inputdir+"/2stocks_group_ret55_120_2.csv"
fama_file = inputdir+"/2fama_factors55_120_2.csv"

def gentbsi(sBSI,gBSI):
    sBSI = np.array(sBSI)
    gBSI = np.array(gBSI)
    return 0.8*sBSI + 0.2*gBSI

def filter(nums):
    return [i for i in nums if i >= 0 else 0]

def normaliza(ndata):
    ndata = np.array(ndata)
    stderr = np.std(ndata,ddof=1)
    ave = np.mean(ndata)
    return (ndata-ave) / stderr
    
def fit_linear(y,X):
    y = np.array(y)
    X = sm.add_constant(X)
    mod = sm.OLS(y,X)
    res = mod.fit()
    return res
    
def out_groups(nums):
    nums = np.array(nums)
    #print(nums)
    #input()
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
        '''if nums[i] > h:
            nums[i] = h
            cnt += 1
        elif nums[i] < l:
            nums[i] = l
            cnt += 1'''
    print("Total out nums:%d"%cnt)
    #input()
    return nums
    
def process_ret(st_ret):
    for col in st_ret.columns:
        st_ret[col] = list(out_groups(st_ret[col]))

if __name__ == "__main__":

    print(ret_file)
    print(fama_file)
    print(start_samples)

    #fama_factors = pd.read_csv(inputdir+"/Fama_French.csv")
    fama_factors = pd.read_csv(fama_file)
    ret_g = pd.read_csv(ret_file)
    #ret_g = pd.read_csv(inputdir+"/RESSET_stock_ret.csv")
    rft_data = pd.read_csv(inputdir+"/rft.csv")
    bsi_data = pd.read_csv(inputdir+"/HS300_MsgBSI.csv")
    g_bsi = pd.read_csv(inputdir+"/g_MsgBSI.csv")
    hs300_return = pd.read_csv(inputdir+"/HS300_returns.csv")
     
    '''groupret = ret_g.groupby(by=['Sizeflg','BMflg'])
    print(groupret.mean())
    portfolios = pd.DataFrame()
    for gname, gdata in groupret:
        print(gname)
        portfolios[str(gname)] = list(gdata['Pdret_tmv'])
        #print(gdata)
    print(portfolios)'''
    
    #factors = hs300_return['close_returns']
    #factors = fama_factors[['Rmrf_tmv','Smb_tmv','Hml_tmv']]
    #factors = fama_factors[['RiskPremium1','SMB1','HML1']][start_samples:]
    factors = fama_factors[['MktRet','SMB','HML']]
    #factors['HML'] = -fama_factors['HML']
    #factors['BSI'] = bsi_data['intMsgBSI']
    #print(factors['MktRet'])
    print(factors)
    for col in factors.columns:
        factors[col] = np.array(factors[col]) - np.array(rft_data['rft_country1'][1:])#[start_samples:])
    #factors = hs300_return['close_returns'] - rft_data['rft_c1']
    #print(factors.mean())
    #exit(0)
    key_col = list(ret_g.columns)
    key_col.remove('date')
    portfolios = ret_g[key_col]
    #print(ret_g)
    factors = factors[start_samples-1:]
    portfolios = portfolios[start_samples-1:]
    
    for col in portfolios.columns:
        portfolios[col] = np.array(portfolios[col]) - np.array(rft_data['rft_country1'][start_samples:])
    
    print(portfolios)
    process_ret(portfolios)
    #process_ret(factors)
    
    print(portfolios.mean())
    #print(ret_g)   
    
    mod = LinearFactorModel(portfolios, factors, risk_free=True)
    res = mod.fit()
    print(res)
    print(res.betas)
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit(cov_type="robust",steps=3)
    print(res)
    print(res.betas)
    print(factors.corr())
    #factors = fama_factors[['SMB','HML']]

    #print(len(portfolios))
    print(len(factors))    
    
    factors['BSI'] = list(out_groups(gentbsi(bsi_data['intMsgBSI'], g_bsi['g_intMsgBSI'])))[start_samples:]
    #print(factors['BSI'])
    print(factors.corr())
       
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit(cov_type='robust',steps=3)
    print(res)
    print(res.betas)
    
    factors['BSI'] = list(out_groups(gentbsi(bsi_data['preMsgBSI'], g_bsi['g_preMsgBSI'])))[start_samples:]
    #print(factors['BSI'])
    print(factors.corr())
    mod = LinearFactorModelGMM(portfolios, factors,risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    
    factors['BSI'] = list(out_groups(gentbsi(bsi_data['preallMsgBSI'], g_bsi['g_preallMsgBSI'])))[start_samples:]
    #print(factors['BSI'])
    print(factors.corr())
    mod = LinearFactorModelGMM(portfolios, factors,risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    
    factors['BSI'] = (list(gentbsi(bsi_data['intMsgBSI'], g_bsi['g_intMsgBSI'])))[start_samples-1:-1]
    #print(factors['BSI'])
    print(factors.corr())
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    
    factors['BSI'] = (list(gentbsi(bsi_data['preallMsgBSI'], g_bsi['g_preallMsgBSI'])))[start_samples-1:-1]
    #print(factors['BSI'])
    print(factors.corr())
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    print(res.full_summary)
    #print(res.risk_premia)
    
    #for i in key_col:
        #print(fit_linear(portfolios[i],factors).summary())
    print(ret_file)
    print(fama_file)
    print(start_samples)