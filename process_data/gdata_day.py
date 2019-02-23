import statsmodels.tsa.stattools as tsa
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import tushare as ts
import pandas as pd
import math, sys
from scipy import interpolate
from datetime import datetime, timedelta
import pylab as pl

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
    
def inter_value(y,xdate,dates):
    y = np.array(y)
    x = []
    for i in range(len(dates)):
        if dates[i] in xdate:
            x.append(i)
    f=interpolate.interp1d(x,y,kind="quadratic")
    xnew = [i for i in range(len(dates))]
    print(xnew)
    ynew=f(xnew)
    #pl.plot(x,y,"ro")
    #pl.plot(xnew,ynew)
    #pl.show()
    return ynew
    
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("python gdata_day.py <inputDir> <outputDir>")
        exit(1)
    inputDir = sys.argv[1]   
    outputDir = sys.argv[2]    

    stocks300 = ts.get_k_data('000300', index=True,start="2015-01-01",end="2018-10-01")
    #print(stocks300)
    
    stock_close = list(stocks300.close)
    close_returns = []
    for i in range(1,len(stock_close)):
        close_returns.append(math.log(stock_close[i] / stock_close[i-1]))
        
    #print(close_returns)
    gdata = pd.read_csv(inputDir+"/gdata.csv")
    #print(gdata)
    pdate = datetime(2014,12,31)
    end_date = datetime(2018,10,1)
    alldates = []
    monthdates = []
    while pdate <= end_date:
        if pdate.day == 1:
            last = pdate - timedelta(days=1)
            monthdates.append(last.strftime("%Y-%m-%d"))
        alldates.append(pdate.strftime("%Y-%m-%d"))
        pdate += timedelta(days=1)
    
    #print(alldates)
    #print(monthdates)
    alldates = alldates[:-1]
        
    cpi = [100]
    iv = [100]
    m1 = [348056.41]
    gdp = [145670.5496]
    m2 = [1228374.81]
    
    for i in gdata.index:
        d = gdata.loc[i]
        cpi.append(d['cpi']/100*cpi[-1])
        iv.append((d['iv']/100+1)*iv[-1])
        m1.append(d['M1'])
        gdp.append(d['gdp'])
        m2.append(d['M2'])
    #print(cpi)
    #print(iv)
    day_gdata = pd.DataFrame()
    day_gdata['date'] = alldates
    day_gdata['cpi'] = inter_value(cpi,monthdates,alldates)
    day_gdata['iv'] = inter_value(iv,monthdates,alldates)
    day_gdata['m1'] = inter_value(m1,monthdates,alldates)
    day_gdata['gdp'] = inter_value(gdp,monthdates,alldates)
    day_gdata['m2'] = inter_value(m2,monthdates,alldates)
    day_gdata.index = alldates
    print(day_gdata)
    day_gdata = day_gdata.loc[stocks300.date]
    day_gdata['HS300_close'] = list(stocks300.close)
    day_gdata['HS300_open'] = list(stocks300.open)
    day_gdata['HS300_volume'] = list(stocks300.volume)
    #print(day_gdata)
    day_gdata.to_csv(outputDir+"/"+"gdata_day.csv",index=False)
    
    exit(0)
    
    '''lndglobal = []
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
    dlngdp = [lngdp[i] - lngdp[i-1] for i in range(1,len(lngdp))]'''
    #print(lncpi)
    #print(lniv)
    #print(lnm1)
    
    ratedata = pd.read_csv(inputDir+"/bank_rate.csv")
    ratedata.index = ratedata['date']
    rates = ratedata['rate7']
    rates_country = np.array(ratedata['rate_country10']) - np.array(ratedata['rate_country1'])
    print(rates_country)
    lnrates = []
    lnr_country = []
    for i in range(len(rates)):
        '''if i == 0:
            lnrates.append(0)
            lnr_country.append(0)
        else:'''
        lnrates.append(math.log(rates[i]))
        #lnr_country.append(math.log(rates_country[i]))
    
    exsdata = pd.read_csv(inputDir+"/exchanges.csv")
    exsdata.index = exsdata['date']
    exchanges = np.array(exsdata['exs'])
    
    data = pd.read_csv(inputDir+"/"+BSI_file)
    data.index = data['date']
    preMsgBSIs = data['preMsgBSI']
    intMsgBSIs = data['intMsgBSI']
    aftMsgBSIs = data['aftMsgBSI']
    preallMsgBSIs = data['preallMsgBSI']
    aftallMsgBSIs = data['aftallMsgBSI']
    preallArgS = data['preallArgS']
    intArgS = data['intArgS']
    
    new_data = pd.DataFrame()
    new_data['HS300_returns'] = close_returns
    #new_data['MsgBSIs'] = list(monthMsgBSIs)
    new_data['rates'] = list(rates)
    new_data['rates_country'] = list(rates_country)
    new_data['exs'] = list(exchanges)
    #new_data['date'] = groupdata.index
    new_data.to_csv('gdata_day.csv',index=False)
    
    print("ADF test for close_returns:")
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
    plt.show()