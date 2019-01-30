import pandas as pd
import datetime
import sys

inputFile = "000069_tiezi.csv"
end = datetime.datetime(2018,10,2)
start = datetime.datetime(2015,1,1) 

if __name__ == "__main__":
    inputFile = sys.argv[1]
    data = pd.read_csv(inputFile)
    data2 = data.groupby(lambda x:str(data.loc[x]['pub_time']).split(' ')[0]).size()
    print(data2)
    now_set = set(data2.index)
    t = start
    all_set = []
    while t != end:
        all_set.append(t.strftime("%Y-%m-%d"))
        t = t + datetime.timedelta(days=1)
    all_set = set(all_set)
    res1 = list(all_set-now_set)
    res1.sort()
    print(res1)
    print(now_set-all_set)
    print(len(data))
    #data2.to_csv('result.csv')
