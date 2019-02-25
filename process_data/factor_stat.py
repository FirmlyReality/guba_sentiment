from linearmodels.asset_pricing import LinearFactorModel
from linearmodels.asset_pricing import LinearFactorModelGMM
import pandas as pd
import numpy as np
import statsmodels.api as sm

inputdir = "../res_data1"

def gentbsi(sBSI,gBSI):
    sBSI = np.array(sBSI)
    gBSI = np.array(gBSI)
    return 0.2*sBSI + 0.8*gBSI

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

if __name__ == "__main__":

    #fama_factors = pd.read_csv(inputdir+"/Fama_French.csv")
    fama_factors = pd.read_csv(inputdir+"/2fama_factors.csv")
    ret_g = pd.read_csv(inputdir+"/2stocks_group_ret.csv")
    #ret_g = pd.read_csv(inputdir+"/mn_stocks_group_ret.csv")
    rft_data = pd.read_csv(inputdir+"/rft.csv")
    bsi_data = pd.read_csv(inputdir+"/HS300_MsgBSI.csv")
    g_bsi = pd.read_csv(inputdir+"/g_MsgBSI.csv")
    hs300_return = pd.read_csv(inputdir+"/HS300_returns.csv")
     
    '''groupret = ret_g.groupby(by=['Sizeflg','BMflg'])
    print(groupret.mean())
    portfolios = pd.DataFrame()
    for gname, gdata in groupret:
        print(gname)
        portfolios[str(gname)] = list(gdata['Pmonret_tmv'])
        #print(gdata)
    print(portfolios)'''
    
    #factors = hs300_return['close_returns']
    #factors = fama_factors[['Rmrf_tmv','Smb_tmv','Hml_tmv']]
    #factors = fama_factors[['RiskPremium1','SMB1','HML1']]
    factors = fama_factors[['MktRet','SMB','HML']]
    #factors['HML'] = -fama_factors['HML']
    #factors['BSI'] = bsi_data['intMsgBSI']
    #print(factors['MktRet'])
    #print(factors.mean())
    factors['MktRet'] = factors['MktRet'] - rft_data['rft_country10']
    #factors = hs300_return['close_returns'] - rft_data['rft_c1']
    print(factors.mean())
    #exit(0)
    key_col = list(ret_g.columns)
    key_col.remove('date')
    portfolios = ret_g[key_col]
    #print(ret_g)
    
    print(portfolios.mean())
    for col in portfolios.columns:
        portfolios[col] = portfolios[col] - rft_data['rft_country10']
    
    print(portfolios.mean())
    #print(ret_g)
    
    
    mod = LinearFactorModel(portfolios, factors,risk_free=True)
    res = mod.fit()
    print(res)
    print(res.betas)
    
    mod = LinearFactorModelGMM(portfolios, factors,risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    
    factors['BSI'] = list(gentbsi(bsi_data['intMsgBSI'], g_bsi['g_intMsgBSI']))
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    
    factors['BSI'] = list(gentbsi(bsi_data['preMsgBSI'], g_bsi['g_preMsgBSI']))
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    
    factors['BSI'] = [0]+list(gentbsi(bsi_data['intMsgBSI'][1:], g_bsi['g_intMsgBSI'][1:]))
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    
    factors['BSI'] = list(gentbsi(bsi_data['preallMsgBSI'], g_bsi['g_preallMsgBSI']))
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit(steps=3)
    print(res)
    print(res.betas)
    print(res.full_summary)
    #print(res.risk_premia)
    
    #for i in key_col:
        #print(fit_linear(portfolios[i],factors).summary())