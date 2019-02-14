import statsmodels.tsa.stattools as tsa
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import tushare as ts
import pandas as pd
import math

BSI_file = "HS300_MsgBSI.csv"

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
    
    new_data = pd.DataFrame()
    new_data['HS300_returns'] = close_returns
    #new_data['date'] = groupdata.index
    new_data.to_csv('month_HS300_returns.csv',index=False)
        
    #print(close_returns)
    gdata = pd.read_csv("gdata.csv")
    #print(gdata)
        
    lncpi = []
    lniv = []
    lnm1 = []
    lngdp = []
    
    lndglobal = []
    for i in gdata.index:
        d = gdata.loc[i]
        lncpi.append(math.log(d['cpi']/100))
        lniv.append(math.log(d['iv']/100.0+1))
        if i == 0:
            lnm1.append(math.log(d['M1']/348056.41))
            lngdp.append(math.log(d['gdp']/145670.5496))
        else:
            lnm1.append(math.log(d['M1']/gdata.loc[i-1]['M1']))
            lngdp.append(math.log(d['gdp']/gdata.loc[i-1]['gdp']))
    
    globals = list(gdata['global'].dropna())
    lndglobal = [globals[i] - globals[i-1] for i in range(1,len(globals))]
    dlngdp = [lngdp[i] - lngdp[i-1] for i in range(1,len(lngdp))]
    #print(lncpi)
    #print(lniv)
    #print(lnm1)
    
    ratedata = pd.read_csv("bank_rate.csv")
    ratedata.index = ratedata['date']
    groupdata = ratedata.groupby(lambda x:ratedata.loc[x]['date'][:7]).mean()
    print(groupdata)
    rates = groupdata['rate7']
    rates_country = groupdata['rate_country']
    lnrates = []
    lnr_country = []
    for i in range(len(rates)):
        '''if i == 0:
            lnrates.append(0)
            lnr_country.append(0)
        else:'''
        lnrates.append(math.log(rates[i]))
        lnr_country.append(math.log(rates_country[i]))
    #exit(0)
    
    data = pd.read_csv(BSI_file)
    data.index = data['date']
    groupdata = data.groupby(lambda x:data.loc[x]['date'][:7]).max()
    print(groupdata)
    preMsgBSIs = groupdata['preMsgBSI']
    intMsgBSIs = groupdata['intMsgBSI']
    aftMsgBSIs = groupdata['aftMsgBSI']
    preallMsgBSIs = groupdata['preallMsgBSI']
    aftallMsgBSIs = groupdata['aftallMsgBSI']
    preallArgS = groupdata['preallArgS']
    intArgS = groupdata['intArgS']
    
    print("ADF test for close_returns:")
    print(tsa.adfuller(close_returns,regression="nc"))
    
    print("ADF test for global:")
    print(tsa.adfuller(lndglobal))
    print(tsa.adfuller(lndglobal,regression="nc"))
    print(tsa.adfuller(lndglobal,regression="ct"))

    #print("ADF test for gdp:")
    #print(tsa.adfuller(gdp))
    
    print("ADF test for dlngdp:")
    print(tsa.adfuller(dlngdp,regression="ct"))
    print(tsa.adfuller(dlngdp,regression="ctt"))
    print(tsa.adfuller(dlngdp,regression="nc"))
    print(tsa.adfuller(dlngdp))
    
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
    
    print("ADF test for rates:")
    print(tsa.adfuller(rates))
    
    print("ADF test for lnrates:")
    print(tsa.adfuller(lnrates))

    print("ADF test for rates_country:")
    print(tsa.adfuller(rates_country))
    
    print("ADF test for lnr_country:")
    print(tsa.adfuller(lnr_country))    
    
    print("ADF test for preallMsgBSIs:")
    print(tsa.adfuller(preallMsgBSIs))

    print("ADF test for aftallMsgBSIs:")
    print(tsa.adfuller(aftallMsgBSIs))      
    
    #fit_linear(close_returns,lncpi)
    #fit_linear(close_returns[1:],lncpi[:-1])
    #fit_linear(close_returns,lniv)
    #fit_linear(close_returns[1:],lniv[1:])
    fit_linear(close_returns[1:],lnm1[1:])
    fit_linear(close_returns[1:],lnm1[:-1])
    fit_linear(close_returns,rates)
    fit_linear(close_returns[1:],rates[:-1])
    #fit_linear(close_returns[1:],dlngdp)
    #fit_linear(close_returns[1:36],globals)
    fit_linear(close_returns,rates_country)
    fit_linear(close_returns[1:],rates_country[:-1])
    #fit_linear(close_returns[1:],lnrates[1:])
    #fit_linear(close_returns,lncpi,lniv,lnm1)
    #fit_linear(close_returns[1:],close_returns[:-1],preallMsgBSIs[1:],preallMsgBSIs[:-1])
    fit_linear(close_returns,lniv,aftallMsgBSIs)
    fit_linear(close_returns,lncpi,aftallMsgBSIs)
    fit_linear(close_returns,lncpi,lniv,aftallMsgBSIs)
    exit(0)
    #print(close_returns)
    #print(preallMsgBSIs)
    fit_linear(close_returns[1:],preallMsgBSIs[:-1])
    fit_linear(close_returns[2:],preallMsgBSIs[:-2])
    fit_linear(close_returns,aftallMsgBSIs)
    fit_linear(close_returns[1:],aftallMsgBSIs[:-1])
    fit_linear(close_returns[2:],aftallMsgBSIs[:-2])
    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plt.plot(preallMsgBSIs.index,aftallMsgBSIs,'b',alpha=0.9)
    plt.plot(preallMsgBSIs.index,close_returns,alpha=0.9)
    #plt.plot(preallMsgBSIs.index[1:],preallMsgBSIs[:-1],alpha=0.9)
    plt.show()