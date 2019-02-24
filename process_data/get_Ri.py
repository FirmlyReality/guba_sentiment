import pandas as pd
import tushare as ts
from datetime import datetime
import numpy as np
import math

input_dir = "../res_data1"
change_freq = 1

def find_idx(nums,val):
    idx = 0
    while idx < len(nums):
        if val <= nums[idx]:
            return idx
        idx += 1
    return idx

if __name__ == "__main__":

    ret_data = pd.read_csv(input_dir+"/CSMAR_stock_ret.csv",dtype={"Stkcd":str})

    ts.set_token('54fb12ea71fa89da0470b68769d417df44df150e981284bec7c42c89')
    
    tspro = ts.pro_api()
    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    date_300 = list(stocks300.date)
    ret_data = ret_data[ret_data['Trdsta']==1]
    
    Rft_list = [["2014-11-22",2.35], ["2015-03-01",2.10], ["2015-05-11",1.85], ["2015-06-28",1.60], ["2015-08-26",1.35], ["2015-10-24",1.10]]
    Rft = []
    last_i = -1
    for date in stocks300.date:
        if last_i < len(Rft_list)-1 and date >= Rft_list[last_i+1][0]:
            last_i += 1
        r = Rft_list[last_i][1]/100
        rr = (r+1)**(1/90)-1
        Rft.append(rr)
    rft_data = pd.DataFrame()
    rft_data['date'] = stocks300.date
    rft_data['rft'] = Rft
    rft_data.to_csv('rft.csv',index=False)
    
    st_group_ret = {}
    for i in range(1,6):
        for j in range(1,6):
            st_group_ret['S'+str(i)+'BM'+str(j)] = []
    
    SMB = []
    HML = []
    mkt_ret = []
    
    ch_day = change_freq
    for date_str in date_300:
        print(date_str)
        date = datetime.strptime(date_str,"%Y-%m-%d")
        ret_d = ret_data[ret_data['Trddt']==date_str]
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
                retdata = ret_d.loc[st_g.index]
                print(retdata[retdata['Dsmvosd'].isna()].index)
                retdata = retdata.dropna()
                sizes = np.array(retdata['Dsmvosd'])
                w = sizes / sum(sizes)
                ret = np.array(retdata['Dretwd'])
                gret = np.sum(w*ret)
                fg[g_name] = gret
            print(fg)
            smb = 1/3*(fg['S1BM1']+fg['S1BM2'] + fg['S1BM3']) - 1/3 * (fg['S2BM1']+fg['S2BM2']+fg['S2BM3'])
            SMB.append(smb)
            hml = 1/2*(fg['S1BM3']+fg['S2BM3']) - 1/2*(fg['S1BM1']+fg['S2BM1'])
            HML.append(hml)
            
            mkt_w = np.array(ret_d['Dsmvosd']) / sum(np.array(ret_d['Dsmvosd']))
            mkt_ret.append(np.sum(mkt_w * np.array(ret_d['Dretwd'])))
            
            size_pers = np.percentile(st_basics['circ_mv'],[20,40,60,80])
            bm_pers = np.percentile(st_basics['BM'],[20,40,60,80])
            #print(size_pers)
            #print(bm_pers)
        
            st_groups = st_basics.groupby(by=ngroups)
        print(st_groups.size())

        for g_name, st_g in st_groups:
            retdata = ret_d.loc[st_g.index]
            print(retdata[retdata['Dsmvosd'].isna()].index)
            retdata = retdata.dropna()
            sizes = np.array(retdata['Dsmvosd'])
            w = sizes / sum(sizes)
            ret = np.array(retdata['Dretwd'])
            gret = np.sum(w*ret)
            st_group_ret[g_name].append(gret)
            
        ch_day += 1
    
    fama_factors = pd.DataFrame()
    fama_factors['date'] = date_300
    fama_factors['MktRet'] = mkt_ret
    fama_factors['SMB'] = SMB
    fama_factors['HML'] = HML
    fama_factors['rft'] = Rft
    fama_factors.to_csv('fama_factors.csv',index=False)
    
    #print(st_group_ret)
    group_ret_data = pd.DataFrame()
    group_ret_data['date'] = date_300
    for k in st_group_ret.keys():
        group_ret_data['ret_'+k] = st_group_ret[k]
    group_ret_data.to_csv('stocks_group_ret.csv',index=False)