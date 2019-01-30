import pandas as pd
import os, sys
import time

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python analysis.py <lengthLimit> <inputDir> <outputDir>")
        exit(1)
    
    lengthLimit = int(sys.argv[1])
    inputDir = sys.argv[2]
    outputDir = sys.argv[3]
    files = sorted(os.listdir(inputDir))
    i = 0
    tiezicnt = 0
    replycnt = 0
    while i < len(files):
       
        dfile = files[i+1]
        print("Filter %s" % dfile)
        data = pd.read_csv(inputDir+"/"+dfile,dtype=str)
        '''alltieziids = set(data['tid'])
        data['length'] = [len(str(data.loc[idx]['content'])) + len(str(data.loc[idx]['title'])) + 1 for idx in data.index]
        data_delete = data[data['length'] > lengthLimit]
        tiezi_delete = set(data_delete['tid'])
        data = data[data['length'] <= lengthLimit]
        data.to_csv(outputDir+"/"+dfile,index=False)'''
        tiezicnt += len(data)
        
        #print(tiezi_delete)
        
        dfile = files[i]
        print("Filter %s" % dfile)
        data = pd.read_csv(inputDir+"/"+dfile,dtype=str)
        '''rpidl = []
        tieziidl = [] 
        authorl = []
        timel = []
        rp2idl = []
        contentl = []
        for idx in data.index:
            d = data.loc[idx]
            if d['tieziid'] not in alltieziids:
                print('Error!!! reply(%s) tiezi(%s) not in data!' %(d['rpid'], d['tieziid']))
                continue
            if d['tieziid'] not in tiezi_delete and len(str(d['content'])) <= lengthLimit:
                rpidl.append(d['rpid'])
                tieziidl.append(d['tieziid'])
                authorl.append(d['author'])
                timel.append(d['time'])
                rp2idl.append(d['rp2id'])
                contentl.append(d['content'])
        data = pd.DataFrame()
        data['rpid'] = rpidl
        data['tieziid'] = tieziidl
        data['author'] = authorl
        data['time'] = timel
        data['rp2id'] = rpidl
        data['content'] = contentl
        data.to_csv(outputDir+"/"+dfile,index=False)'''
        replycnt += len(data)
        
        i += 2
    
    print("tiezicnt: "+str(tiezicnt))
    print("replycnt: "+str(replycnt))