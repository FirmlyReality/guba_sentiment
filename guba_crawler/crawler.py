import pandas as pd
import traceback
from function import *

start_time = "2015-01-01 00:00:00"
end_time = "2018-10-01 15:30:00"
fail_limit = 200
resultDir = "result2/"
code_input = "stock_list.txt"

def get_data(code,fail_limit,start_time,end_time,start_page=1,start_year=2018):
    if start_page == 1:
        first_reply = True
        first_tiezi = True
    else:
        first_reply = False
        first_tiezi = False
    
    
    year = start_year
    fail_cnt = 0
    crawled_tiezi = set()
    for page in range(start_page,20000):
        print("Get Code:"+code+" page:"+str(page))
        pub_time_list = []
        content_list = []
        title_list = []
        ptiezi_data = get_guba_list(code,page)
        index_list = list(ptiezi_data.index)
            
        del_list = []
        end_flag = False
        new_uptime_list = []
        for i in range(len(index_list)):
            nidx = index_list[i]
            if nidx in crawled_tiezi:
                print("Tiezi %s has been crawled." % nidx)
                del_list.append(nidx)
                continue
            crawled_tiezi.add(nidx)
            rowdata = ptiezi_data.loc[nidx]
            pub_time, title, content, data = get_guba_tiezi(nidx,str(rowdata['replys']),str(rowdata['url']),start_time,end_time)
            
            if pub_time is not None:
                now_year = int(pub_time.split('-')[0])
                if now_year >= year - 1:
                    year = now_year
                now_time = str(now_year) + "-" + str(rowdata['update_time']) +":00"
            else:
                now_time = str(year) + "-" + str(rowdata['update_time']) +":00"
            update_time = str(year) + "-" + str(rowdata['update_time']) +":00"
            print("updatetime: " + update_time + " now_time: " + now_time + " fail_cnt:" + str(fail_cnt))
            if update_time < start_time:
                del_list.append(nidx)
                fail_cnt += 1
                continue
            else:
                fail_cnt = 0
            if title is None:
                del_list.append(nidx)
                continue
            
            new_uptime_list.append(update_time)
            pub_time_list.append(pub_time)
            content_list.append(content)
            title_list.append(title)
            
            if first_reply:
                data.to_csv(resultDir+code+"_reply.csv")
                first_reply = False
            else:
                data.to_csv(resultDir+code+"_reply.csv",mode="a",header=False)
        
        
        ptiezi_data = ptiezi_data.drop(del_list,inplace=False)
        ptiezi_data['title'] = title_list
        ptiezi_data['pub_time'] = pub_time_list
        ptiezi_data['content'] = content_list
        ptiezi_data['update_time'] = new_uptime_list
        #print(ptiezi_data)
        
        if first_tiezi:
            ptiezi_data.to_csv(resultDir+code+"_tiezi.csv")
            first_tiezi = False
        else:
            ptiezi_data.to_csv(resultDir+code+"_tiezi.csv",mode="a",header=False)
        #print(tiezi_data)
        
        if fail_cnt >= fail_limit:
            print(fail_cnt)
            return page, year

if __name__ == "__main__":
    code_file = open(code_input,"r")
    code_list = code_file.read()
    for line in code_list.split('\n'):
        if line == "":
            continue
        lines = line.split(' ')
        code = lines[0]
        date_list = []
        for i in range(1,len(lines),4):
            date_list.append([lines[i]+" "+lines[i+1],lines[i+2]+" "+lines[i+3]])
        page = 1
        year = 2018
        for dates in date_list:
            start_time = dates[0]
            end_time = dates[1]
            print()
            print("Get data from: "+code+" start_time:"+start_time+" end_time:"+end_time)
            print("start_page: "+str(page)+" start_year: "+str(year))
            print()
            page,year = get_data(code,fail_limit,start_time,end_time,page,year)
            page -= 4