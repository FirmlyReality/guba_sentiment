import pandas as pd
import os, sys
import time
import collections

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analysis.py <inputDir>")
        exit(1)
    
    starttime = time.time()
    inputDir = sys.argv[1]
    files = os.listdir(inputDir)
    tiezi_lencount = collections.Counter()
    reply_lencount = collections.Counter()
    tiezicnt = 0
    replyscnt = 0
    stocks_crawled = set()
    for dfile in files:
        print("Read from %s" % dfile)
        code = dfile.split('_')[0]
        stocks_crawled.add(code)
        ftype = dfile.split('_')[1].split('.')[0]
        data = pd.read_csv(inputDir+"/"+dfile,dtype=str)
        print("Groupby ...")
        if ftype == "reply":
            #lendata = data.groupby(lambda x:len(str(data.loc[x]['content']))).size()
            lendata = [len(str(c)) for c in data['content']]
            lencount = reply_lencount
        else:
            #lendata = data.groupby(lambda x:len(str(data.loc[x]['content'])+str(data.loc[x]['title']))+1).size()
            lendata = [len(str(data.loc[i]['content'])) + len(str(data.loc[i]['title'])) + 1 for i in data.index]
            lencount = tiezi_lencount
        lencount.update(lendata)
        '''for lenidx in lendata.index:
            if lenidx not in lencount:
                lencount[lenidx] = lendata[lenidx]
            else:
                lencount[lenidx] += lendata[lenidx]'''
        
        if ftype == 'tiezi':
            tiezicnt += len(data)
        else:
            replyscnt += len(data)
        
        #print(lencount)
    
    print(time.time()-starttime)
    tiezi_df = pd.DataFrame.from_dict(dict(tiezi_lencount), orient='index')
    tiezi_df.rename(columns={0:'tiezicnt'},inplace=True)
    reply_df = pd.DataFrame.from_dict(dict(reply_lencount), orient='index')
    reply_df.rename(columns={0:'replycnt'},inplace=True)
    lencntdf = tiezi_df.join(reply_df,how="outer",sort=True)
    print(lencntdf)
    lencntdf.to_csv('lencnt.csv',index=True)
    
    '''allcnt = tiezicnt + replyscnt
    now = 0
    for lenidx in lencntdf.index:
        now += lencount[lenidx]
        if now > 0.95*allcnt:
            print("length %d is on 0.95" % (lenidx))
            print("now=%d allcnt=%d"%(now,allcnt))
            break'''
    
    print("Total tiezi count: "+str(tiezicnt))
    print("Total reply count: "+str(replyscnt))
    
    print("Read from need_stock.txt and build stocks_need set...")
    stockfile = open("need_stock.txt")
    stocks_need = set()
    lines = stockfile.read().splitlines()
    stockfile.close()
    for l in lines:
        lsplits = l.split()
        code = lsplits[0]
        if code in stocks_need:
            print("Error! code exists!")
            exit(1)
        stocks_need.add(code)
    print("Need but not crawled: ")
    print(str(stocks_need-stocks_crawled))
    print("Crawled but not need: ")
    print(str(stocks_crawled-stocks_need))
        