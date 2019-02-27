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

if __name__ == "__main__":

    ret_data = pd.read_csv(input_dir+"/CSMAR_stock_ret.csv",dtype={"Stkcd":str})
    
    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    date_300 = list(stocks300.date)
    ret_data = ret_data[ret_data['Trdsta']==1]
    ret_data = ret_data[(ret_data['Markettype']==1)|(ret_data['Markettype']==4)]
    ret_data2 = ret_data.set_index(['Trddt','Stkcd'])
    ret_data = ret_data.set_index(['Stkcd','Trddt'])
    stocks_basics = pd.read_csv("stocks_basics.csv",dtype={"ts_code":str,"trade_date":str})
    stocks_basics = stocks_basics.set_index(['trade_date','ts_code'])
    BSI_data = pd.read_csv("../res_data1/HS300_MsgBSI.csv")
    gBSI_data = pd.read_csv("../res_data1/g_MsgBSI.csv")
    fBSI = 0.8*BSI_data['preallMsgBSI'] + 0.2*gBSI_data['g_preallMsgBSI']
    #print(stocks_basics)
    print(fBSI)
    
    st_group_ret = {}
    for i in range(1,sizegroups+1):
        for j in range(1,bmgroups+1):
            for k in range(1,sentgroups+1):
                st_group_ret['S'+str(i)+'BM'+str(j)+'E'+str(k)] = []
            
    fama_factors = pd.read_csv("2fama_factors10.csv")[["date","MktRet","SMB","HML"]]
    fama_factors['BSI'] = fBSI
    fama_factors = fama_factors.set_index(['date'])
    window_dates = []
    init_dates = date_300[:startdays]
    for sdate_str in init_dates:
        sdate = datetime.strptime(sdate_str,"%Y-%m-%d").strftime("%Y%m%d")
        window_dates.append(sdate)
    st_basics = stocks_basics.loc[window_dates]

    st_basics_groups = st_basics.groupby(by=['ts_code'])
    st_basics_cnt = st_basics_groups.size()
    print(st_basics_cnt)
    betas = []
    for code in st_basics_cnt.index:
        '''try:
            st_ret = ret_data.loc[code]
            st_ret = st_ret.loc[init_dates].dropna()
        except Exception as err:
            #print(err)
            betas.append(None)
            continue
        if len(st_ret) <= windowsize/2:
            betas.append(None)
            continue
        ret_dates = st_ret.index
        st_ret = st_ret['Dretwd']
        factors = fama_factors.loc[ret_dates]
        #print(code)
        res = fit_linear(st_ret,factors)
        betas.append(res.params[-1])'''
        betas.append(1)
    
    #exit(0)
    st_basics = st_basics.groupby(by=['ts_code']).mean()
    st_basics['Beta'] = betas
    st_basics = st_basics.dropna()
            
    size_pers = np.percentile(st_basics['circ_mv'],[50])
    bm_pers = np.percentile(st_basics['BM'],[33.3,66.7])
    betas_pers = np.percentile(st_basics['Beta'],[100])
    print(st_basics['Beta'])
    print(betas_pers)
            
    def ngroups(i):
        d = st_basics.loc[i]
        i1 = find_idx(size_pers,d['circ_mv'])
        i2 = find_idx(bm_pers,d['BM'])
        i3 = find_idx(betas_pers,d['Beta'])
        return 'S'+ str(i1+1) + "BM" + str(i2+1) + "E" + str(i3+1)
                
    factors_groups = st_basics.groupby(by=ngroups)
            
    size_pers = np.percentile(st_basics['circ_mv'],[100/sizegroups*i for i in range(1,sizegroups)])
    bm_pers = np.percentile(st_basics['BM'],[100/bmgroups*i for i in range(1,bmgroups)])
    betas_pers = np.percentile(st_basics['Beta'],[100/sentgroups*i for i in range(1,sentgroups)])
        
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
        smb = 1/3*(fg['S1BM1E1']+fg['S1BM2E1'] + fg['S1BM3E1']) - 1/3 * (fg['S2BM1E1']+fg['S2BM2E1']+fg['S2BM3E1'])
        fama_d['SMB'] = smb
        hml = 1/2*(fg['S1BM3E1']+fg['S2BM3E1']) - 1/2*(fg['S1BM1E1']+fg['S2BM1E1'])
        fama_d['HML'] = hml
        
        mkt_w = np.array(ret_d['Dsmvosd']) / sum(np.array(ret_d['Dsmvosd']))
        fama_d['MktRet'] = np.sum(mkt_w * np.array(ret_d['Dretwd']))

        for g_name, st_g in st_groups:
            #print(g_name)
            #print(st_g)
            retdata = ret_d.loc[st_g.index]
            #print(retdata[retdata['Dsmvosd'].isna()].index)
            retdata = retdata.dropna()
            sizes = np.array(retdata['Dsmvosd'])
            w = sizes / sum(sizes)
            ret = np.array(retdata['Dretwd'])
            gret = np.sum(w*ret)
            st_group_ret[g_name].append(gret)
        
        ch_day += 1
        cnt_days += 1
            
        if ch_day == change_freq:
            ch_day = 0
            print("Change groups")
           
            st_basics = stocks_basics.loc[window_dates]
            group_basics = st_basics.groupby(by=['ts_code'])
            st_basics = group_basics.mean()
            
            st_basics_groups = st_basics.groupby(by=['ts_code'])
            st_basics_cnt = st_basics_groups.size()
            #print(st_basics_cnt)
            betas = []
            for code in st_basics_cnt.index:
                '''try:
                    st_ret = ret_data.loc[code]
                    date_idx = date_300.index(date_str)
                    st_ret = st_ret.loc[date_300[date_idx-windowsize+1:date_idx+1]].dropna()
                except Exception as err:
                    #print(err)
                    betas.append(None)
                    continue
                if len(st_ret) <= windowsize/2:
                    betas.append(None)
                    continue
                ret_dates = st_ret.index
                st_ret = st_ret['Dretwd']
                factors = fama_factors.loc[ret_dates]
                #print(code)
                res = fit_linear(st_ret,factors)
                betas.append(res.params[-1])'''
                betas.append(1)
            st_basics['Beta'] = betas
            st_basics = st_basics.dropna()            
            
            size_pers = np.percentile(st_basics['circ_mv'],[50])
            bm_pers = np.percentile(st_basics['BM'],[33.3,66.7])
            #sprint(st_basics)
            betas_pers = np.percentile(st_basics['Beta'],[100])
            #print(betas_pers)
            
            def ngroups(i):
                d = st_basics.loc[i]
                i1 = find_idx(size_pers,d['circ_mv'])
                i2 = find_idx(bm_pers,d['BM'])
                i3 = find_idx(betas_pers,d['Beta'])
                return 'S'+ str(i1+1) + "BM" + str(i2+1) + "E" + str(i3+1)
                
            factors_groups = st_basics.groupby(by=ngroups)
            
            size_pers = np.percentile(st_basics['circ_mv'],[100/sizegroups*i for i in range(1,sizegroups)])
            bm_pers = np.percentile(st_basics['BM'],[100/bmgroups*i for i in range(1,bmgroups)])
            betas_pers = np.percentile(st_basics['Beta'],[100/sentgroups*i for i in range(1,sentgroups)])
            #print(size_pers)
            #print(bm_pers)
        
            st_groups = st_basics.groupby(by=ngroups)

    fama_factors = fama_factors[startdays:enddays]
    fama_factors['date'] = date_300[startdays:enddays]
    fama_factors.to_csv('3fama_factors551_30.csv',index=False)
    
    #print(st_group_ret)
    group_ret_data = pd.DataFrame()
    #group_ret_data['date'] = date_300[startdays:enddays]
    for k in st_group_ret.keys():
        print(len(st_group_ret[k]))
        group_ret_data['ret_'+k] = st_group_ret[k]
    group_ret_data.to_csv('3stocks_group_ret551_30.csv',index=False)