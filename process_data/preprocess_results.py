import pandas as pd
import numpy as np
import os, sys, math
from datetime import datetime, timedelta


need_stocks = ['000002']
origin_dir = "../../../data/filter_data1"
results_dir = "../../../data/results"
output_dir = "../../../data/sum_results"

def get_time_data(data,stime,etime):
    sdata = data[(data['time']>=stime) & (data['time'] < etime)]
    #print(sdata)
    data0 = sdata[sdata['content_classes'] == 0]
    data1 = sdata[sdata['content_classes'] == 1]
    data2 = sdata[sdata['content_classes'] == 2]
    data3 = sdata[sdata['content_classes'] == 3]
    #cnt = len(data1) + len(data2) + len(data3)
    prob0_sum = sum(data0['content_prob'])
    prob1_sum = sum(data1['content_prob'])
    prob2_sum = sum(data2['content_prob'])
    prob3_sum = sum(data3['content_prob'])
    return [len(data0),prob0_sum], [len(data1),prob1_sum], [len(data2),prob2_sum], [len(data3),prob3_sum]

if __name__ == "__main__":
    for code in need_stocks:
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
                content_prob.append(max(rdata))
            i += 1
        
        tiezidata['title_classes'] = title_classes
        tiezidata['title_prob'] = title_prob
        tiezidata['content_classes'] = content_classes
        tiezidata['content_prob'] = content_prob
        
        result_file = open(results_dir+"/"+code+"_reply.tsv")
        content_classes = []
        content_prob = []
        for line in result_file.read().splitlines():
            rdata = line.split('\t')
            rdata = [float(f) for f in rdata]
            content_classes.append(rdata.index(max(rdata)))
            content_prob.append(max(rdata))
        
        replydata['content_classes'] =  content_classes
        replydata['content_prob'] = content_prob
        
        print("Group by time and write to file...")
        start_date = datetime.strptime('2015-01-01 9:30:00',"%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime('2018-10-01 9:30:00',"%Y-%m-%d %H:%M:%S")          
        
        stime = start_date
        etime = start_date+timedelta(hours=5,minutes=30)
        datesl = []
        aft_stat = {'tiezi':[],'reply':[]}
        int_stat = {'tiezi':[],'reply':[]}
        while stime < end_date:
            print("stime:%s etime:%s"%(stime.strftime("%Y-%m-%d %H:%M:%S"), etime.strftime("%Y-%m-%d %H:%M:%S")))
            datesl.append(etime.strftime("%Y-%m-%d"))
            intt = get_time_data(tiezidata, stime.strftime("%Y-%m-%d %H:%M:%S"), etime.strftime("%Y-%m-%d %H:%M:%S"))
            int_stat['tiezi'].append(intt)
            #print(intt)
            intr = get_time_data(replydata, stime.strftime("%Y-%m-%d %H:%M:%S"), etime.strftime("%Y-%m-%d %H:%M:%S"))
            int_stat['reply'].append(intr)
            #print(intr)
             
            stime = stime + timedelta(days=1)
            print("stime:%s etime:%s"%(etime.strftime("%Y-%m-%d %H:%M:%S"), stime.strftime("%Y-%m-%d %H:%M:%S")))
            aftert = get_time_data(tiezidata, etime.strftime("%Y-%m-%d %H:%M:%S"), stime.strftime("%Y-%m-%d %H:%M:%S"))
            aft_stat['tiezi'].append(aftert)
            #print(aftert)
            afterr = get_time_data(replydata, etime.strftime("%Y-%m-%d %H:%M:%S"), stime.strftime("%Y-%m-%d %H:%M:%S"))
            aft_stat['reply'].append(afterr)
            #print(afterr)
            etime = etime + timedelta(days=1)
            
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
        
        print(indicat_data)
        indicat_data.to_csv(output_dir+"/"+code+".csv",index=False)