import pandas as pd
import tushare as ts
from datetime import datetime
import numpy as np
import math

input_dir = "../res_data1"
change_freq = 1
computemonth = 46

def find_idx(nums,val):
    idx = 0
    while idx < len(nums):
        if val <= nums[idx]:
            return idx
        idx += 1
    return idx

if __name__ == "__main__":

    ret_data = pd.read_csv(input_dir+"/CSMAR_stret_month.csv",dtype={"Stkcd":str},sep="\t")

    ts.set_token('54fb12ea71fa89da0470b68769d417df44df150e981284bec7c42c89')
    
    tspro = ts.pro_api()
    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    groupdata = stocks300.groupby(lambda x:stocks300.loc[x].date[:7])
    date_300 = list(groupdata.tail(1).date)
    print(date_300)
    #ret_data = ret_data[ret_data['Trdsta']==1]
    ret_data = ret_data[(ret_data['Markettype']==1)|(ret_data['Markettype']==4)]
    ret_data = ret_data.dropna()
    #print(ret_data[ret_data['Msmvosd'].isna()].index)
    
    st_group_ret = {}
    for i in range(1,6):
        for j in range(1,6):
            st_group_ret['S'+str(i)+'BM'+str(j)] = []
    
    SMB = []
    HML = []
    mkt_ret = []
    
    ch_day = change_freq
    last_close = pd.DataFrame
    for date_str in date_300[:computemonth]:
        print(date_str)
        date = datetime.strptime(date_str,"%Y-%m-%d")
        date_month = date_str[:7]
        ret_d = ret_data[ret_data['Trdmnt']==date_month]
        #print(ret_d[ret_d['Msmvosd'].isna()].index)
        ret_d.index = list(ret_d['Stkcd'])
        
        if ch_day == change_freq:
            ch_day = 0
            print("Change groups")
            all_stocks = list(ret_d['Stkcd'])
            ret_d.index = all_stocks
            
            st_basics = tspro.daily_basic(ts_code='', trade_date=date.strftime("%Y%m%d"), fields='ts_code,pb,total_mv,circ_mv')
            st_basics.index = [st_basics.loc[i]['ts_code'][:-3] for i in st_basics.index]
            st_basics = st_basics.loc[all_stocks]
            print(st_basics[st_basics['circ_mv'].isna()])
            st_basics = st_basics.dropna()
            
            st_basics['BM'] = [1/st_basics.loc[i]['pb'] for i in st_basics.index]
            
            size_pers = np.percentile(st_basics['circ_mv'],[50])
            bm_pers = np.percentile(st_basics['BM'],[33.3,66.7])
            
            def ngroups(i):
                d = st_basics.loc[i]
                i1 = find_idx(size_pers,d['circ_mv'])
                i2 = find_idx(bm_pers,d['BM'])
                return 'S'+ str(i1+1) + "BM" + str(i2+1)
                       
            st_groups = st_basics.groupby(by=ngroups)
            fg = {}
            for g_name, st_g in st_groups:
                #print(g_name)
                #print(st_g)
                retdata = ret_d.loc[st_g.index]
                print(retdata[retdata['Msmvosd'].isna()].index)
                retdata = retdata.dropna()
                sizes = np.array(retdata['Msmvosd'])
                w = sizes / sum(sizes)
                ret = np.array(retdata['Mretwd'])
                gret = np.sum(w*ret)
                fg[g_name] = gret
            print(fg)
            smb = 1/3*(fg['S1BM1']+fg['S1BM2'] + fg['S1BM3']) - 1/3 * (fg['S2BM1']+fg['S2BM2']+fg['S2BM3'])
            SMB.append(smb)
            hml = 1/2*(fg['S1BM3']+fg['S2BM3']) - 1/2*(fg['S1BM1']+fg['S2BM1'])
            HML.append(hml)
            
            print(ret_d[ret_d['Mretwd'].isna()])
            mkt_w = np.array(ret_d['Msmvosd']) / sum(np.array(ret_d['Msmvosd']))
            mkt_ret.append(np.sum(mkt_w * np.array(ret_d['Mretwd'])))
            
            size_pers = np.percentile(st_basics['circ_mv'],[20,40,60,80])
            bm_pers = np.percentile(st_basics['BM'],[20,40,60,80])
            #print(size_pers)
            #print(bm_pers)
        
            st_groups = st_basics.groupby(by=ngroups)
        print(st_groups.size())

        for g_name, st_g in st_groups:
            #print(g_name)
            #print(st_g)
            retdata = ret_d.loc[st_g.index]
            print(retdata[retdata['Msmvosd'].isna()].index)
            retdata = retdata.dropna()
            sizes = np.array(retdata['Msmvosd'])
            w = sizes / sum(sizes)
            ret = np.array(retdata['Mretwd'])
            gret = np.sum(w*ret)
            st_group_ret[g_name].append(gret)
            
        ch_day += 1
    
    fama_factors = pd.DataFrame()
    fama_factors['date'] = date_300[:computemonth]
    fama_factors['MktRet'] = mkt_ret
    fama_factors['SMB'] = SMB
    fama_factors['HML'] = HML
    fama_factors.to_csv('mn_fama_factors.csv',index=False)
    
    #print(st_group_ret)
    group_ret_data = pd.DataFrame()
    group_ret_data['date'] = date_300[:computemonth]
    for k in st_group_ret.keys():
        group_ret_data['ret_'+k] = st_group_ret[k]
    group_ret_data.to_csv('mn_stocks_group_ret.csv',index=False)