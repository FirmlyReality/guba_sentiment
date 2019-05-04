import pandas as pd
import tushare as ts
from datetime import datetime
import numpy as np
import math
import statsmodels.api as sm

input_dir = "../res_data1"
change_freq = 30
startdays = 60
enddays = 915
windowsize = startdays
mktgroups = 5
sizegroups = 5
bmgroups = 5
sentgroups = 1

def find_idx(nums,val):
    idx = 0
    while idx < len(nums):
        if val <= nums[idx]:
            return idx
        idx += 1
    return idx
    
def fit_linear(y,X):
    y = np.array(y)
    X = sm.add_constant(np.array(X))
    mod = sm.OLS(y,X)
    res = mod.fit()
    return res
    
def return_betas(ret_data,st_basics_stg,fama_factors,reg_dates,windowsize):
    betas = []
    for code in st_basics_stg.index:
        try:
            st_ret = ret_data.loc[code]
            st_ret = st_ret.loc[reg_dates].dropna()
        except Exception as err:
            betas.append([None]*5)
            continue
        if len(st_ret) <= 20:
            betas.append([None]*5)
            continue
        ret_dates = st_ret.index
        st_ret = st_ret['Dretwd']
        factors = fama_factors.loc[ret_dates]
        res = fit_linear(st_ret,factors)
        betas.append(list(res.params))
    return betas

if __name__ == "__main__":

    ret_data = pd.read_csv(input_dir+"/CSMAR_stock_ret.csv",dtype={"Stkcd":str})
    
    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    date_300 = list(stocks300.date)
    ret_data = ret_data[ret_data['Trdsta']==1]
    ret_data = ret_data[(ret_data['Markettype']==1)|(ret_data['Markettype']==4)]
    ret_data2 = ret_data.set_index(['Trddt','Stkcd'])
    ret_data = ret_data.set_index(['Stkcd','Trddt'])
    stocks_basics = pd.read_csv("stocks_basics.csv",dtype={"ts_code":str,"trade_date":str})
    stocks_basics = stocks_basics.set_index(['trade_date'])
    BSI_data = pd.read_csv("../res_data1/HS300_MsgBSI.csv")
    gBSI_data = pd.read_csv("../res_data1/g_MsgBSI.csv")
    fBSI = 0.8*BSI_data['preallMsgBSI'] + 0.2*gBSI_data['g_preallMsgBSI']
    #print(stocks_basics)
    print(fBSI)
    
    st_group_ret = {}
    for i0 in range(1,mktgroups+1):
        for i in range(1,sizegroups+1):
            for j in range(1,bmgroups+1):
                for k in range(1,sentgroups+1):
                    st_group_ret['M'+str(i0)+'S'+str(i)+'BM'+str(j)+'E'+str(k)] = []
            
    fama_factors = pd.read_csv("2fama_factors120.csv")[["date","MktRet","SMB","HML"]]
    fama_factors['BSI'] = fBSI
    fama_factors = fama_factors.set_index(['date'])
    window_dates = []
    init_dates = date_300[:startdays]
    for sdate_str in init_dates:
        sdate = datetime.strptime(sdate_str,"%Y-%m-%d").strftime("%Y%m%d")
        window_dates.append(sdate)
    st_basics = stocks_basics.loc[window_dates]
    print(st_basics)
    #input()
    
    st_basics = st_basics.groupby(by=['ts_code']).tail(1)
    print(st_basics)
    #input()
    st_basics.index = list(st_basics['ts_code'])
    betas = return_betas(ret_data,st_basics,fama_factors,init_dates,windowsize)
    print(betas)
    st_basics['MktBeta'] = [b[1] for b in betas]
    st_basics['SBeta'] = [b[4] for b in betas]
    print(st_basics)
    st_basics = st_basics.dropna()
    print(st_basics)
    #input()
            
    size_pers = np.percentile(st_basics['circ_mv'],[50])
    bm_pers = np.percentile(st_basics['BM'],[33.3,66.7])
    mkt_pers = np.percentile(st_basics['MktBeta'],[100])
    sent_pers = np.percentile(st_basics['SBeta'],[100])
    #print(st_basics['Beta'])
    #print(betas_pers)
            
    def ngroups(i):
        d = st_basics.loc[i]
        i0 = find_idx(mkt_pers,d['MktBeta'])
        i1 = find_idx(size_pers,d['circ_mv'])
        i2 = find_idx(bm_pers,d['BM'])
        i3 = find_idx(sent_pers,d['SBeta'])
        return 'M'+str(i0+1)+'S'+ str(i1+1) + "BM" + str(i2+1) + "E" + str(i3+1)
                
    factors_groups = st_basics.groupby(by=ngroups)
    
    mkt_pers = np.percentile(st_basics['MktBeta'],[100/mktgroups*i for i in range(1,mktgroups)])    
    size_pers = np.percentile(st_basics['circ_mv'],[100/sizegroups*i for i in range(1,sizegroups)])
    bm_pers = np.percentile(st_basics['BM'],[100/bmgroups*i for i in range(1,bmgroups)])
    sent_pers = np.percentile(st_basics['SBeta'],[100/sentgroups*i for i in range(1,sentgroups)])
        
    st_groups = st_basics.groupby(by=ngroups)
           
    ch_day = 0
    last_date = []
    cnt_days = startdays
    all_stocks = ret_data.index[0]
    for date_str in date_300[startdays:enddays]:
        print(date_str)
        date = datetime.strptime(date_str,"%Y-%m-%d")
        ret_d = ret_data2.loc[date_str]
        #ret_data = ret_data[ret_data['Trdsta']==1]
        #ret_d.index = list(ret_d['Stkcd'])
        window_dates = window_dates[1:] + [date.strftime("%Y%m%d")]

        print(factors_groups.mean())
        print(st_groups.mean())
        
        fg = {}
        for g_name, st_g in factors_groups:
            retdata = ret_d.loc[st_g.index]
            #print(retdata[retdata['Dsmvosd'].isna()].index)
            retdata = retdata.dropna()
            sizes = np.array(retdata['Dsmvosd'])
            w = sizes / sum(sizes)
            ret = np.array(retdata['Dretwd'])
            gret = np.sum(w*ret)
            fg[g_name] = gret
            print(gret)
        print(fg)
        fama_d = fama_factors.loc[date_str]
        smb = 1/3*(fg['M1S1BM1E1']+fg['M1S1BM2E1'] + fg['M1S1BM3E1']) - 1/3 * (fg['M1S2BM1E1']+fg['M1S2BM2E1']+fg['M1S2BM3E1'])
        fama_d['SMB'] = smb
        hml = 1/2*(fg['M1S1BM3E1']+fg['M1S2BM3E1']) - 1/2*(fg['M1S1BM1E1']+fg['M1S2BM1E1'])
        fama_d['HML'] = hml
        
        mkt_w = np.array(ret_d['Dsmvosd']) / sum(np.array(ret_d['Dsmvosd']))
        fama_d['MktRet'] = np.sum(mkt_w * np.array(ret_d['Dretwd']))
        
        has_set = set()
        for g_name, st_g in st_groups:
            has_set.add(g_name)
            try:
                retdata = ret_d.loc[st_g.index]
            except Exception as err:
                print(err)
                st_group_ret[g_name].append(0.0)
                continue
            retdata = retdata.dropna()
            sizes = np.array(retdata['Dsmvosd'])
            w = sizes / sum(sizes)
            ret = np.array(retdata['Dretwd'])
            gret = np.sum(w*ret)
            st_group_ret[g_name].append(gret)
        has_set = set(st_group_ret.keys()) - has_set
        for g_name in has_set:
            st_group_ret[g_name].append(0)
        
        ch_day += 1
        cnt_days += 1
            
        if ch_day == change_freq:
            ch_day = 0
            print("Change groups")
           
            st_basics = stocks_basics.loc[window_dates]
            group_basics = st_basics.groupby(by=['ts_code'])
            st_basics = group_basics.tail(1)
            st_basics.index = list(st_basics['ts_code'])
            
            date_idx = date_300.index(date_str)
            betas = return_betas(ret_data,st_basics,fama_factors,date_300[date_idx-windowsize+1:date_idx+1],windowsize)
            st_basics['MktBeta'] = [b[1] for b in betas]
            st_basics['SBeta'] = [b[4] for b in betas]
            print(st_basics)
            st_basics = st_basics.dropna()
            print(st_basics)
            #input()         
            
            size_pers = np.percentile(st_basics['circ_mv'],[50])
            bm_pers = np.percentile(st_basics['BM'],[33.3,66.7])
            mkt_pers = np.percentile(st_basics['MktBeta'],[100])
            sent_pers = np.percentile(st_basics['SBeta'],[100])
            #print(st_basics['Beta'])
            #print(betas_pers)
                    
            def ngroups(i):
                d = st_basics.loc[i]
                i0 = find_idx(mkt_pers,d['MktBeta'])
                i1 = find_idx(size_pers,d['circ_mv'])
                i2 = find_idx(bm_pers,d['BM'])
                i3 = find_idx(sent_pers,d['SBeta'])
                return 'M'+str(i0+1)+'S'+ str(i1+1) + "BM" + str(i2+1) + "E" + str(i3+1)
                        
            factors_groups = st_basics.groupby(by=ngroups)
            
            mkt_pers = np.percentile(st_basics['MktBeta'],[100/mktgroups*i for i in range(1,mktgroups)])    
            size_pers = np.percentile(st_basics['circ_mv'],[100/sizegroups*i for i in range(1,sizegroups)])
            bm_pers = np.percentile(st_basics['BM'],[100/bmgroups*i for i in range(1,bmgroups)])
            sent_pers = np.percentile(st_basics['SBeta'],[100/sentgroups*i for i in range(1,sentgroups)])
                
            st_groups = st_basics.groupby(by=ngroups)

    fama_factors = fama_factors[startdays:enddays]
    fama_factors['date'] = date_300[startdays:enddays]
    fama_factors.to_csv('3fama_factors5551_60.csv',index=False)
    
    #print(st_group_ret)
    group_ret_data = pd.DataFrame()
    #group_ret_data['date'] = date_300[startdays:enddays]
    for k in st_group_ret.keys():
        print(len(st_group_ret[k]))
        group_ret_data['ret_'+k] = st_group_ret[k]
    group_ret_data.to_csv('3stocks_group_ret5551_60.csv',index=False)