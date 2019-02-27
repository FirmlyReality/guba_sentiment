from linearmodels.asset_pricing import LinearFactorModel
from linearmodels.asset_pricing import LinearFactorModelGMM
import pandas as pd
import numpy as np
import statsmodels.api as sm
import math

inputdir = "../res_data1"

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
    
    
def FamaMacBeth(st_ret,X):
    time_res = []
    for col in st_ret.columns:
        print(len(st_ret[col]))
        print(len(X))
        time_res.append(fit_linear(st_ret[col],X))
        print(time_res[-1].summary())
    #res = fit_linear(st_ret,X)
    #print(res.summary())
    #print(res.param)
    res_params = []
    for res in time_res:
        res_params.append(res.params[1:])
    res_params = np.array(res_params)
    res_params = sm.add_constant(res_params)
    print(res_params)
    
    cross_sec_params = []
    cov = st_ret.cov()
    print(cov)
    
    print(st_ret)
    for t in st_ret.index:
        d = np.array(st_ret.loc[t])
        res = sm.GLS(d,res_params,sigma=cov).fit()
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
        std = np.std(cs_params[i])
        print(np.mean(cs_params[i]))
        print(np.std(cs_params[i]))
        print(m/(std/math.sqrt(len(X))))

if __name__ == "__main__":

    fama_factors = pd.read_csv(inputdir+"/RESSET_mn_Fama_French.csv")
    #fama_factors = pd.read_csv(inputdir+"/2fama_factors602.csv")
    #ret_g = pd.read_csv(inputdir+"/2stocks_group_ret.csv")
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
    
    factors = fama_factors[['Rmrf_tmv']]
    #factors = fama_factors[['RiskPremium1','SMB1','HML1']]
    #factors = fama_factors[['MktRet','SMB','HML']]
    #factors['HML'] = -fama_factors['HML']
    #factors['BSI'] = bsi_data['intMsgBSI']
    #print(factors['MktRet'])
    #factors['MktRet'] = factors['MktRet'] - rft_data['rft_country1']
    #print(factors.mean())
    #factors = hs300_return['close_returns'] - list(rft_data['rft_country1'])
    #factors = factors
    #print(factors)
    #exit(0)
    #key_col = list(ret_g.columns)
    #key_col.remove('date')
    #portfolios = ret_g[key_col]
    print(portfolios)
    #print(ret_g)
    
    for col in portfolios.columns:
        portfolios[col] = portfolios[col] #- 0.005
    
    #print(ret_g)
    
    
    FamaMacBeth(portfolios,factors)