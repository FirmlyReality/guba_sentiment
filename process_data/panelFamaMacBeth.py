import pandas as pd
from linearmodels.panel import FamaMacBeth
from linearmodels.panel import PooledOLS
from linearmodels.panel import PanelOLS
import statsmodels.api as sm

inputdir="../res_data1"

if __name__ == "__main__":
    stret = pd.read_csv("eviews_stret.csv")
    FamaFactors = pd.read_csv("2fama_factors602.csv")
    bsi_data = pd.read_csv(inputdir+"/HS300_MsgBSI.csv")
    
    
    timels = [i for i in range(1,915)]*25
    typels = ["S"+str(i)+"BM"+str(j) for i in range(1,6) for j in range(1,6) for k in range(914)]
    
    stret['time'] = timels
    stret['type'] = typels
    
    FamaFactors['MktRet'] = FamaFactors['MktRet'] - FamaFactors['rft']
    
    ff = FamaFactors[["MktRet","SMB","HML"]]
    factors = pd.DataFrame()
    for i in range(25):
        factors = pd.concat([factors,ff],ignore_index=False)
    
    stret = stret.set_index(['type','time'])
    factors['time'] = timels
    factors['type'] = typels
    factors = factors.set_index(['type','time'])
    stret = stret["0"]
    print(stret)
    print(factors)
    
    
    mod = PanelOLS(stret,factors,entity_effects=True)
    res = mod.fit()
    print(res)