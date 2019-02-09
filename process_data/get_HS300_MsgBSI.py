import pandas as pd
import os
import tushare as ts
from datetime import datetime

BSI_dir = "../../../data/MsgBSI_data"
stocks_weight_file = "../../weights300.csv"
stocks_change_file = "../../stock_date.csv"

#def get_weights(weights_data,)

if __name__ == "__main__":
    
    stocks_BSI = {}
    print("Read from BSI_dir(%s) and build stocks_BSI..."%BSI_dir)
    files = os.listdir(BSI_dir)
    
    for file in files:
        code = file.split(".")[0]
        data = pd.read_csv(os.path.join(BSI_dir,file))
        data.index = data['date']
        data.drop('date',axis=1,inplace=True)
        stocks_BSI[code] = data
    
    #print(stocks_BSI)
    
    print("Read from stocks_weight_file(%s)...")
    weights_data = pd.read_csv(stocks_weight_file)
    weights_data.index = [s[:6] for s in weights_data['order_book_id']]
    #print(weights_data)
    
    print("Read from stocks_change_file(%s)...")
    change_data = pd.read_csv(stocks_change_file)
    change_data = change_data[change_data['stat'] == '纳入']
    change_date = sorted(list(set(change_data['date'])))
    #print(change_date)
    
    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    date_300 = list(stocks300.date)
    #print(date_300)
    
    #print([d in date_300 for d in change_date])
    
    last_month = 0
    for date_str in date_300:
        print(date_str)
        date = datetime.strptime(date_str,"%Y-%m-%d")
        if date.month != last_month or date_str in change_date:
            print("Weights Update!!!")
            y = date.year
            m = date.month
            if date_str in change_date:
                if m == 12:
                    m = 1
                    y += 1
                else:
                    m += 1
            wdate = datetime(y,m,1).strftime("%Y%m%d")
            now_weights = weights_data[wdate].dropna()
            print(now_weights)
        
        #exit(0)
    
    
    