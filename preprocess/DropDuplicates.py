import pandas as pd
import os,sys

if __name__ == "__main__":
    
    if len(sys.argv) < 3:
        print("python DropDuplicates.py inputDir outputDir")
        exit(1)
    inputDir = sys.argv[1]
    outputDir = sys.argv[2]

    print("Read from need_stock.txt and build stock_date dict...")
    stockfile = open("need_stock.txt")
    stock_date = {}
    lines = stockfile.read().splitlines()
    stockfile.close()
    for l in lines:
        lsplits = l.split()
        code = lsplits[0]
        if code in stock_date.keys():
            print("Error! code exists!")
            exit(1)
        stock_date[code] = []
        lsplits = lsplits[1:]
        i = 0
        while i < len(lsplits):
            stock_date[code].append([lsplits[i]+" "+lsplits[i+1],lsplits[i+2]+" "+lsplits[i+3]])
            i += 4
        if i == 0:
            stock_date[code].append(["2015-01-01 00:00:00","2018-10-01 15:30:00"])
    
    '''for code in stock_date.keys():
        outlist = [code]
        for date in stock_date[code]:
            outlist.append(date[0])
            outlist.append(date[1])
        print(" ".join(outlist))'''
    #print(stock_date)
    
    print("Read from inputDir %s" % inputDir)
    files = os.listdir(inputDir)
    outfiles = os.listdir(outputDir)
    for dfile in files:
        print("Read from %s" % dfile)
        code = dfile.split('_')[0]
        ftype = dfile.split('_')[1].split('.')[0]
        if code not in stock_date.keys():
            print("Error! Code does not exist!")
            exit(1)
        data = pd.read_csv(inputDir+"/"+dfile,dtype=str)
        firstc = data.columns[0]
        if ftype == "tiezi":
            idname = "tid"
        else:
            idname = "rpid"
        data.rename(columns={firstc:idname,'pub_time':'time'},inplace=True)
        print("Before drop: %d" % len(data))
        data.drop_duplicates([idname],inplace=True)
        print("After drop: %d" % len(data))
        
        '''if ftype == "reply":
            data.drop_duplicates(['tieziid','author','content'],inplace=True)
        else:
            data0 = data[data['replys'] == '0']
            data0 = data0.drop_duplicates(['title','content','author'])
            #print(data0)
            data1 = data[data['replys'] != '0']
            data = pd.concat([data0,data1])
            #print(data1)
        print("After drop duplicated content: %d" % len(data))
        #print(data)'''
        
        if len(stock_date[code]) == 2:
            time1 = stock_date[code][0]
            time2 = stock_date[code][1]
            data = data[ ((data['time']>=time1[0])&(data['time']<=time1[1])) | ((data['time']>=time2[0])&(data['time']<=time2[1])) ]
        else:
            time1 = stock_date[code][0]
            data = data[(data['time']>=time1[0])&(data['time']<=time1[1])]
        print("After filter time: %d" % len(data))
        
        if dfile in outfiles:
            print("Output File exists!!")
            exit(1)
        print("Write new file to %s" % (outputDir + "/"+dfile))
        data.to_csv(outputDir+"/"+dfile,index=False)
        
