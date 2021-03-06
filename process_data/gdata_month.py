import statsmodels.tsa.stattools as tsa
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import tushare as ts
import pandas as pd
import math

data_dir = "../res_data1/"
BSI_file = data_dir + "HS300_MsgBSI.csv"

def fit_linear(y,*X):
    Xs = []
    for x in X:
        assert len(x) == len(y)
        Xs.append(np.array(x))
    #print(Xs)
    x = np.array(Xs).T
    #print(x)
    y = np.array(y)
    X = sm.add_constant(np.array(x))
    mod = sm.OLS(y,X)
    res = mod.fit()
    print(res.summary())
    
if __name__ == "__main__":

    stocks300 = ts.get_k_data('000300', index=True,start="2014-12-01",end="2018-10-01")
    #print(stocks300)

    groupdata = stocks300.groupby(lambda x:stocks300.loc[x].date[:7])
    monthp = groupdata.mean()
    print(monthp)
    
    stock_close = list(monthp.close)
    print(monthp.close)
    close_returns = []
    for i in range(1,len(monthp.close)):
        close_returns.append(math.log(stock_close[i] / stock_close[i-1]))
        
    #print(close_returns)
    gdata = pd.read_csv(data_dir+"gdata.csv")
    #print(gdata)
        
    lncpi = []
    lniv = []
    lnm1 = []
    lngdp = []
    lnm2 = []
    
    lndglobal = []
    for i in gdata.index:
        d = gdata.loc[i]
        lncpi.append(math.log(d['cpi']/100))
        lniv.append(math.log(d['iv']))
        if i == 0:
            lnm1.append(math.log(d['M1']/348056.41))
            lngdp.append(math.log(d['gdp']/145670.5496))
            lnm2.append(math.log(d['M2']/1228374.81))
        else:
            lnm1.append(math.log(d['M1']/gdata.loc[i-1]['M1']))
            lngdp.append(math.log(d['gdp']/gdata.loc[i-1]['gdp']))
            lnm2.append(math.log(d['M2']/gdata.loc[i-1]['M2']))
    
    globals = list(gdata['global'].dropna())
    lndglobal = [globals[i] - globals[i-1] for i in range(1,len(globals))]
    dlngdp = [lngdp[i] - lngdp[i-1] for i in range(1,len(lngdp))]
    #print(lncpi)
    #print(lniv)
    #print(lnm1)
    
    ratedata = pd.read_csv(data_dir+"bank_rate.csv")
    ratedata.index = ratedata['date']
    groupdata = ratedata.groupby(lambda x:ratedata.loc[x]['date'][:7]).mean()
    print(groupdata)
    rates = groupdata['rate7']
    rates_country = np.array(groupdata['rate_country10']) - np.array(groupdata['rate_country1'])
    print(rates_country)
    '''lnrates = []
    lnr_country = []
    for i in range(len(rates)):
        if i == 0:
            lnrates.append(0)
            lnr_country.append(0)
        else:
        lnrates.append(math.log(rates[i]))
        #lnr_country.append(math.log(rates_country[i]))
    #exit(0)'''
    
    exsdata = pd.read_csv(data_dir+"exchanges.csv")
    exsdata.index = exsdata['date']
    groupdata = exsdata.groupby(lambda x:exsdata.loc[x]['date'][:7]).mean()
    exchanges = np.array(groupdata['exs'])
    
    data = pd.read_csv(data_dir+BSI_file)
    data['all'] = [data.loc[i]['preMsgBSI'] + data.loc[i]['intMsgBSI'] for i in data.index]
    data.index = data['date']
    groupdata = data.groupby(lambda x:data.loc[x]['date'][:7]).mean()
    print(groupdata)
    '''preMsgBSIs = groupdata['preMsgBSI']
    intMsgBSIs = groupdata['intMsgBSI']
    aftMsgBSIs = groupdata['aftMsgBSI']
    preallMsgBSIs = groupdata['preallMsgBSI']
    aftallMsgBSIs = groupdata['aftallMsgBSI']
    preallArgS = groupdata['preallArgS']
    intArgS = groupdata['intArgS']'''
    monthMsgBSIs = groupdata['all'] / 2
    
    data = pd.read_csv(data_dir+"g_MsgBSI.csv")
    data['all'] = [data.loc[i]['g_preMsgBSI'] + data.loc[i]['g_intMsgBSI'] for i in data.index]
    data.index = data['date']
    groupdata = data.groupby(lambda x:data.loc[x]['date'][:7]).mean()
    print(groupdata)
    g_monthMsgBSIs = groupdata['all'] / 2
    
    bdata = pd.read_csv(data_dir+"HS300_mv_pb_pe.csv",dtype={"ts_code":str,"trade_date":str})
    bdata.index = bdata['trade_date']
    print(bdata.index)
    groupdata = bdata.groupby(lambda x:bdata.loc[x]['trade_date'][:6]).mean()
    print(groupdata)
    
    new_data = pd.DataFrame()
    new_data['HS300_returns'] = close_returns
    new_data['MsgBSIs'] = list(monthMsgBSIs)
    new_data['g_MsgBSIs'] = list(g_monthMsgBSIs)
    new_data['rates'] = list(rates)
    new_data['rates_country'] = list(rates_country)
    new_data['exs'] = list(exchanges)
    new_data['total_mv'] = list(groupdata['total_mv'])
    new_data['float_mv'] = list(groupdata['float_mv'])
    new_data['B/M'] = list(1.0/groupdata['pb'])
    new_data['pe'] = list(groupdata['pe'])
    #new_data['date'] = groupdata.index
    new_data.to_csv(data_dir+'monthdata_Ret_BSI.csv',index=False)
    
    '''print("ADF test for close_returns:")
    print(tsa.adfuller(close_returns,regression="nc"))
    
    print("ADF test for global:")
    print(tsa.adfuller(lndglobal))
    print(tsa.adfuller(lndglobal,regression="nc"))
    print(tsa.adfuller(lndglobal,regression="ct"))

    #print("ADF test for gdp:")
    #print(tsa.adfuller(gdp))
    
    print("ADF test for lngdp:")
    print(tsa.adfuller(lngdp,regression="ct"))
    print(tsa.adfuller(lngdp,regression="ctt"))
    print(tsa.adfuller(lngdp,regression="nc"))
    print(tsa.adfuller(lngdp))
    
    print("ADF test for lncpi:")
    print(tsa.adfuller(lncpi))
        
    print("ADF test for lniv:")
    print(tsa.adfuller(lniv))
    print(tsa.adfuller(lniv,regression="ct"))
    print(tsa.adfuller(lniv,regression="ctt"))
    print(tsa.adfuller(lniv,regression="nc"))
 
    print("ADF test for m1:")
    print(tsa.adfuller(gdata['M1']))
 
    print("ADF test for lnm1:")
    print(tsa.adfuller(lnm1))
    
    print("ADF test for m2:")
    print(tsa.adfuller(gdata['M2']))    
    
    print("ADF test for lnm2:")
    print(tsa.adfuller(lnm2))
    
    print("ADF test for rates:")
    print(tsa.adfuller(rates))
    
    print("ADF test for lnrates:")
    print(tsa.adfuller(lnrates))

    print("ADF test for rates_country:")
    print(tsa.adfuller(rates_country,regression="nc"))
    print(tsa.adfuller(rates_country))
    
    #print("ADF test for lnr_country:")
    #print(tsa.adfuller(lnr_country))

    #print("ADF test for lnr_country:")
    #print(tsa.adfuller(lnr_country))

    print("ADF test for exchanges:")
    print(tsa.adfuller(exchanges)) 
    print(tsa.adfuller(exchanges,regression="nc"))
    print(tsa.adfuller(exchanges,regression="ct"))    
    
    print("ADF test for preallMsgBSIs:")
    print(tsa.adfuller(preallMsgBSIs))

    print("ADF test for aftallMsgBSIs:")
    print(tsa.adfuller(aftallMsgBSIs))

    print("ADF test for monthMsgBSIs:")
    print(tsa.adfuller(monthMsgBSIs))     
    
    #fit_linear(close_returns,lncpi)
    #fit_linear(close_returns[1:],lncpi[:-1])
    #fit_linear(close_returns,lniv)
    #fit_linear(close_returns[1:],lniv[1:])
    #fit_linear(close_returns,lnm2)
    #fit_linear(close_returns[1:],lnm2[:-1])
    #fit_linear(close_returns[:-1],lnm2[1:])
    fit_linear(close_returns,rates_country)
    fit_linear(close_returns[1:],rates_country[:-1])
    fit_linear(close_returns[:-1],rates_country[1:])
    fit_linear(close_returns,lngdp)
    fit_linear(close_returns[1:],lngdp[:-1])
    fit_linear(close_returns[:-1],lngdp[1:])
    #fit_linear(close_returns[1:36],globals)
    fit_linear(close_returns,rates_country)
    fit_linear(close_returns[1:],rates_country[:-1])
    #fit_linear(close_returns[1:],lnrates[1:])
    #fit_linear(close_returns,lncpi,lniv,lnm1)
    #fit_linear(close_returns[1:],close_returns[:-1],preallMsgBSIs[1:],preallMsgBSIs[:-1])
    fit_linear(close_returns,monthMsgBSIs)
    fit_linear(close_returns,lncpi,monthMsgBSIs)
    fit_linear(close_returns,lniv,monthMsgBSIs)
    fit_linear(close_returns,lncpi,lniv,monthMsgBSIs)
    #print(close_returns)
    #print(preallMsgBSIs)
    fit_linear(close_returns[1:],preallMsgBSIs[:-1])
    fit_linear(close_returns[2:],preallMsgBSIs[:-2])
    fit_linear(close_returns,aftallMsgBSIs)
    fit_linear(close_returns[1:],aftallMsgBSIs[:-1])
    fit_linear(close_returns[2:],aftallMsgBSIs[:-2])
    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plt.plot(preallMsgBSIs.index,monthMsgBSIs,'b',alpha=0.9)
    plt.plot(preallMsgBSIs.index,close_returns,alpha=0.9)
    #plt.plot(preallMsgBSIs.index[1:],preallMsgBSIs[:-1],alpha=0.9)
    plt.show()'''