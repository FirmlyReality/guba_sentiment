import pandas as pd
import numpy as np
import os, sys, math
from datetime import datetime, timedelta
import time

need_stocks = []
data_dir = "../../../data"
origin_dir = data_dir + "/filter_data1"
results_dir = data_dir + "/results"
output_dir = data_dir + "/sum_results"
rp_results_dir = data_dir + "/rp_results"

def get_time_data(sdata):
    #sdata = filter_data(data,stime,etime)
    #print(sdata)
    data0 = sdata[sdata['content_classes'] == 0]
    data1 = sdata[sdata['content_classes'] == 1]
    data2 = sdata[sdata['content_classes'] == 2]
    data3 = sdata[sdata['content_classes'] == 3]
    #cnt = len(data1) + len(data2) + len(data3)
    prob0_sum = sum(data0['content_prob_0'])
    prob1_sum = sum(data1['content_prob_1'])
    prob2_sum = sum(data2['content_prob_2'])
    prob3_sum = sum(data3['content_prob_3'])
    return [len(data0),prob0_sum], [len(data1),prob1_sum], [len(data2),prob2_sum], [len(data3),prob3_sum]

def get_reply_prob(tdata, replydata, rpdata, now_sum):
    #tdata.index = tdata['tid']
    #rpdata.index = rpdata['rpid']
    rpdata = rpdata[(rpdata['content_classes'] == 0) & (rpdata['reply_classes'] != 0)]
    #print(rpdata)
    for i in rpdata.index:
        rp = rpdata.loc[i]
        #print(rp)
        #print(now_sum)
        if not pd.isna(rp['rp2id']):
            if rp['rp2id'] not in replydata.index:
                continue
            rp0 = replydata.loc[rp['rp2id']]
            #print(rp0)
            if rp0['content_classes'] == 0:
                continue
            class0 = rp0['content_classes']
            prob0 = rp0['content_prob_'+str(class0)]
        elif rp['tieziid'] in tdata.index:
            tiezi0 = tdata.loc[rp['tieziid']]
            #print(tiezi0)
            class0 = tiezi0['content_classes']
            prob0 = tiezi0['content_prob_'+str(class0)]
        else:
            continue
        if rp['reply_classes'] == 2:
            now_sum[class0][0] += 1
            now_sum[class0][1] += prob0 #* rp['reply_prob']
        elif rp['reply_classes'] == 1:
            if class0 == 1:
                class0 = 3
            elif class0 == 3:
                class0 = 1
            else:
                continue
            now_sum[class0][0] += 1
            now_sum[class0][1] += prob0 #* rp['reply_prob']
        #print(now_sum)
                
            
    
def filter_data(data,stime,etime):
    data = data[(data['time']>=stime) & (data['time'] < etime)]
    #data0 = data[data['author'] == "上海网友"]
    #data1 = data[data['author'] != "上海网友"]
    #data1 = data1.drop_duplicates(['author','content'])
    #data = pd.concat([data0,data1])
    data = data.drop_duplicates(['author','content'])
    return data

if __name__ == "__main__":

    print("Read from %s/need_stocks.txt and build need_stocks list" % data_dir)
    need_stocks_file = open(data_dir+"/need_stocks.txt")
    for line in need_stocks_file.read().splitlines():
        lined = line.split(' ')
        need_stocks.append(lined[0])
    need_stocks.sort()
    print(need_stocks)
    need_stocks.remove('600832')

    for code in need_stocks[453:]:
        print("Read from %s..."%(code + "_tiezi.csv"))
        tiezidata = pd.read_csv(origin_dir+"/"+code + "_tiezi.csv",dtype=str)
        print("Read from %s..."%(code + "_reply.csv"))
        replydata = pd.read_csv(origin_dir+"/"+code + "_reply.csv",dtype=str)
        
        print("Read results and build new DataFrame...")
        result_file = open(results_dir+"/"+code+"_tiezi.tsv")
        content_classes = []
        content_prob = []
        title_classes = []
        title_prob = []
        i = 0
        for line in result_file.read().splitlines():
            rdata = line.split('\t')
            rdata = [float(f) for f in rdata]
            if i % 2 == 0:
                title_classes.append(rdata.index(max(rdata)))
                title_prob.append(max(rdata))
            else:
                content_classes.append(rdata.index(max(rdata)))
                content_prob.append(rdata)
            i += 1
        
        tiezidata['title_classes'] = title_classes
        tiezidata['title_prob'] = title_prob
        tiezidata['content_classes'] = content_classes
        tiezidata['content_prob_0'] = [p[0] for p in content_prob]
        tiezidata['content_prob_1'] = [p[1] for p in content_prob]
        tiezidata['content_prob_2'] = [p[2] for p in content_prob]
        tiezidata['content_prob_3'] = [p[3] for p in content_prob]
        
        result_file = open(results_dir+"/"+code+"_reply.tsv")
        content_classes = []
        content_prob = []
        for line in result_file.read().splitlines():
            rdata = line.split('\t')
            rdata = [float(f) for f in rdata]
            content_classes.append(rdata.index(max(rdata)))
            content_prob.append(rdata)
        
        replydata['content_classes'] =  content_classes
        replydata['content_prob_0'] = [p[0] for p in content_prob]
        replydata['content_prob_1'] = [p[1] for p in content_prob]
        replydata['content_prob_2'] = [p[2] for p in content_prob]
        replydata['content_prob_3'] = [p[3] for p in content_prob]
        
        rp_result_file = open(rp_results_dir+"/"+code+"_reply.tsv")
        reply_classes = []
        reply_prob = []
        for line in rp_result_file.read().splitlines():
            rdata = line.split('\t')
            rdata = [float(f) for f in rdata]
            reply_classes.append(rdata.index(max(rdata)))
            reply_prob.append(max(rdata))
        
        replydata['reply_classes'] = reply_classes
        replydata['reply_prob'] = reply_prob
        #print(replydata)
        
        replydata.index = replydata['rpid']
        tiezidata.index = tiezidata['tid']
        
        print("Group by time and write to file...")
        start_date = datetime.strptime('2015-01-01 09:30:00',"%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime('2018-10-01 09:30:00',"%Y-%m-%d %H:%M:%S")
        
        stime = start_date
        etime = start_date+timedelta(hours=5,minutes=30)
        datesl = []
        aft_stat = {'tiezi':[],'reply':[]}
        int_stat = {'tiezi':[],'reply':[]}
        pstart_time = time.time()
        i = 0
        while stime < end_date:
            if i % 100 == 0:
                print("stime:%s etime:%s"%(stime.strftime("%Y-%m-%d %H:%M:%S"), etime.strftime("%Y-%m-%d %H:%M:%S")))
            datesl.append(etime.strftime("%Y-%m-%d"))
            tdata = filter_data(tiezidata, stime.strftime("%Y-%m-%d %H:%M:%S"), etime.strftime("%Y-%m-%d %H:%M:%S"))
            intt = get_time_data(tdata)
            int_stat['tiezi'].append(intt)
            #print(intt)
            rpdata = filter_data(replydata, stime.strftime("%Y-%m-%d %H:%M:%S"), etime.strftime("%Y-%m-%d %H:%M:%S"))
            intr = get_time_data(rpdata)
            get_reply_prob(tiezidata, replydata, rpdata, intr)
            int_stat['reply'].append(intr)
            #print(intr)
             
            stime = stime + timedelta(days=1)
            #print("stime:%s etime:%s"%(etime.strftime("%Y-%m-%d %H:%M:%S"), stime.strftime("%Y-%m-%d %H:%M:%S")))
            tdata = filter_data(tiezidata, etime.strftime("%Y-%m-%d %H:%M:%S"), stime.strftime("%Y-%m-%d %H:%M:%S"))
            aftert = get_time_data(tdata)
            aft_stat['tiezi'].append(aftert)
            #print(aftert)
            rpdata = filter_data(replydata, etime.strftime("%Y-%m-%d %H:%M:%S"), stime.strftime("%Y-%m-%d %H:%M:%S"))
            afterr = get_time_data(rpdata)
            get_reply_prob(tiezidata, replydata, rpdata, afterr)
            aft_stat['reply'].append(afterr)
            #print(afterr)
            etime = etime + timedelta(days=1)
            i += 1
        
        indicat_data = pd.DataFrame()
        indicat_data['date'] = datesl
        indicat_data.index = datesl
        for i in range(4):
            indicat_data['int_t_'+str(i)+'_cnt'] = [s[i][0] for s in int_stat['tiezi']]
            indicat_data['int_t_'+str(i)+'_prob'] = [s[i][1] for s in int_stat['tiezi']]
        for i in range(4):
            indicat_data['int_r_'+str(i)+'_cnt'] = [s[i][0] for s in int_stat['reply']]
            indicat_data['int_r_'+str(i)+'_prob'] = [s[i][1] for s in int_stat['reply']]
        for i in range(4):
            indicat_data['aft_t_'+str(i)+'_cnt'] = [s[i][0] for s in aft_stat['tiezi']]
            indicat_data['aft_t_'+str(i)+'_prob'] = [s[i][1] for s in aft_stat['tiezi']]
        for i in range(4):
            indicat_data['aft_r_'+str(i)+'_cnt'] = [s[i][0] for s in aft_stat['reply']]
            indicat_data['aft_r_'+str(i)+'_prob'] = [s[i][1] for s in aft_stat['reply']]      
        
        #print(indicat_data)
        indicat_data.to_csv(output_dir+"/"+code+".csv",index=False)
        print("Time: %f"%(time.time()-pstart_time))