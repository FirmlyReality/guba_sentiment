import pandas as pd

data = pd.read_csv('samples1.csv',dtype=str)
data = data[:4470]
#print(data)
res_file = open("test_results.tsv")
results = []
for line in res_file.read().splitlines():
    d = line.split('\t')
    results.append([float(f) for f in d])
r0 = [r[0] for r in results]
r1 = [r[1] for r in results]
r2 = [r[2] for r in results]
r3 = [r[3] for r in results]

data['p0'] = r0
data['p1'] = r1
data['p2'] = r2
data['p3'] = r3

labels = []
corrects = []
i = 0
for idx in data.index:
    d = data.loc[idx]
    label1 = d['是否股评相关']
    label2 = d['明天以后看好程度']
    if label1 == '0':
        label = 0
    elif label2 == '1' or label2 =='2':
        label = 1
    elif label2 == '3':
        label = 2
    elif label2 == '4' or label2 == '5':
        label = 3
    corrects.append(label == results[i].index(max(results[i])))
    i += 1

max_probs = [max(r) for r in results]
data['corrects'] = corrects
data['max_probs'] = max_probs
data = data.sort_values(by=['corrects','max_probs'],ascending=[True,False])
data.to_csv("test_results.csv",index=False)