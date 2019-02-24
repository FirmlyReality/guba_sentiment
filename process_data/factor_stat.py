from linearmodels.asset_pricing import LinearFactorModel
from linearmodels.asset_pricing import LinearFactorModelGMM
import pandas as pd
import numpy as np

inputdir = "../res_data1"

def gentbsi(sBSI,gBSI):
    sBSI = np.array(sBSI)
    gBSI = np.array(gBSI)
    return sBSI

def normaliza(ndata):
    ndata = np.array(ndata)
    stderr = np.std(ndata)
    ave = np.mean(ndata)
    return (ndata-ave) / stderr

if __name__ == "__main__":

    fama_factors = pd.read_csv(inputdir+"/Fama_French.csv")
    ret_g = pd.read_csv(inputdir+"/stocks_group_ret.csv")
    rft_data = pd.read_csv(inputdir+"/rft.csv")
    bsi_data = pd.read_csv(inputdir+"/HS300_MsgBSI.csv")
    g_bsi = pd.read_csv(inputdir+"/g_MsgBSI.csv")
       
    factors = fama_factors[['RiskPremium1','SMB1']]
    #factors['BSI'] = bsi_data['intMsgBSI']
    print(factors)
    key_col = list(ret_g.columns)
    key_col.remove('date')
    #print(ret_g)
    
    #for col in key_col:
        #ret_g[col] = ret_g[col] - rft_data['rft']
    
    #print(ret_g)
    portfolios = ret_g[key_col]
    
    mod = LinearFactorModel(portfolios, factors)
    res = mod.fit()
    print(res)
    print(res.betas)
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit()
    print(res)
    print(res.betas)
    
    stdbsi = normaliza(gentbsi(bsi_data['intMsgBSI'], g_bsi['g_intMsgBSI']))
    #print(stdbsi)
    factors['BSI'] = stdbsi
    #print(factors['BSI'])
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit()
    print(res)
    print(res.betas)
    
    factors['BSI'] = list(normaliza(gentbsi(bsi_data['preMsgBSI'], g_bsi['g_preMsgBSI'])))
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit()
    print(res)
    print(res.betas)
    
    factors['BSI'] = list(normaliza(gentbsi(bsi_data['preallMsgBSI'], g_bsi['g_preallMsgBSI'])))
    
    mod = LinearFactorModelGMM(portfolios, factors, risk_free=True)
    res = mod.fit()
    print(res)
    print(res.betas)