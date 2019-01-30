import pandas as pd
import os, sys, math
import tushare as ts

stocks = ts.get_stock_basics()['name']
stocks.loc['600005'] = '武钢股份'
stocks.loc['000024'] = '招商地产'
stocks.loc['000562'] = '宏源证券'
stocks.loc['601299'] = '中国北车'
'''file = open("stocks_name.txt","w")
for code in stocks.index:
    file.write(code+"\t"+stocks[code]+"\n")
file.close()'''
    
samples_tid = []
samples_rpid = []
samples_code = []
samples_name = []
samples_time = []
samples_type = []
samples_content = []
def add_samples(tid,rpid,code,name,time,stype,content):
    samples_tid.append(tid)
    samples_rpid.append(rpid)
    samples_code.append(code)
    samples_name.append(name)
    samples_time.append(time)
    samples_type.append(stype)
    samples_content.append(content)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python trainsample.py <smaples> <totalcnt> <inputDir>")
        exit(1)
        
    samplesnum = int(sys.argv[1])
    totalcnt = int(sys.argv[2])
    inputDir = sys.argv[3]
    files = os.listdir(inputDir)
    
    '''for dfile in files:
        code = dfile.split('_')[0]
        if code not in stocks.index:
            print("Error! code %s does not exist!"%code)
    exit(0)'''
    labeled_cnt = {"title":{},"content":{},"reply":{}}
    old_samples = pd.read_csv("samples1.csv",dtype=str)
    cnt = 0
    for i in old_samples.index:
        d = old_samples.loc[i]
        code = d['code']
        if code not in labeled_cnt[d['type']].keys():
            labeled_cnt[d['type']][code] = 0
        labeled_cnt[d['type']][code] += 1
        cnt += 1
    print(labeled_cnt)
    print(cnt)
    

    for dfile in files:
        print("Read from %s" % dfile)
        code = dfile.split('_')[0]
        ftype = dfile.split('_')[1].split('.')[0]
        data = pd.read_csv(inputDir+"/"+dfile,dtype=str)
        if ftype == 'tiezi':
            thisnum = len(data)*2 / totalcnt * samplesnum
            
            title_num = math.floor(thisnum/2)
            print("It'll sample %d title" % title_num)
            if code in labeled_cnt['title'].keys():
                print("stock %s has %d labeled titles" %(code, labeled_cnt['title'][code]) )
                title_num -= labeled_cnt['title'][code]
            if title_num == 0:
                title_num = 1
            print("It'll sample %d title" % title_num)
            if title_num >= 0:
                samples_data = data.sample(n=title_num)
                for idx in samples_data.index:
                    d = samples_data.loc[idx]
                    add_samples(d['tid'],'',code,stocks[code],d['time'],'title',str(d['title']))
            
            content_num = math.ceil(thisnum/2)
            print("It'll sample %d content" % content_num)
            if code in labeled_cnt['content'].keys():
                print("stock %s has %d labeled contents" %(code, labeled_cnt['content'][code]) )
                content_num -= labeled_cnt['content'][code]
            print("It'll sample %d content" % content_num)
            if content_num >= 0:
                samples_data = data.sample(n=content_num)
                for idx in samples_data.index:
                    d = samples_data.loc[idx]
                    add_samples(d['tid'],'',code,stocks[code],d['time'],'content',str(d['title'])+' '+str(d['content']))
        else:
            thisnum = round(len(data) / totalcnt * samplesnum)
            print("It'll sample %d replys" % thisnum)
            if code in labeled_cnt['reply'].keys():
                print("stock %s has %d labeled replys" %(code, labeled_cnt['reply'][code]) )
                thisnum -= labeled_cnt['reply'][code]
            if thisnum == 0:
                thisnum += 1
            print("It'll sample %d replys" % thisnum)
            if thisnum >= 0:
                samples_data = data.sample(n=thisnum)
                for idx in samples_data.index:
                    d = samples_data.loc[idx]
                    add_samples(d['tieziid'],d['rpid'],code,stocks[code],d['time'],'reply',str(d['content']))
                
    samples_data = pd.DataFrame()
    samples_data['tid'] = samples_tid
    samples_data['rpid'] = samples_rpid
    samples_data['code'] = samples_code
    samples_data['name'] = samples_name
    samples_data['time'] = samples_time
    samples_data['type'] = samples_type
    samples_data['content'] = samples_content
    samples_data = samples_data.sample(frac=1)
    samples_data.to_csv('samples.csv',index=False)