#!/usr/bin/env pythonw2.7
import datetime
import yahoo as ya
import numpy as np
import picloud as pc
import logging

class portfolio:
    def __init__(self, symbols, shares, times, cash):
        self.cash = cash
        self.symbols = map(lambda x: x.strip().upper(), symbols)
        self.shares  = map(int, shares)
        self.shares.append(float(cash))
        self.times   = map(lambda x: datetime.datetime.strptime(x, "%Y%m%d").date(), times)
        self.start   = min(self.times) 
        raw = map(lambda x: self._yahoo(x, self.start), self.symbols)
        
        self.symbols.append('RISKFREE')
        self.price   = map(lambda x: x['adj'], raw)
        self.covariance()
        self.marketTime = raw[0]['date']
        self.days = len(self.marketTime)
        rskfree = np.ones(self.days) * (1 + 0.06/365)
        self.price.append(np.cumprod( rskfree))
        self.shares = np.matrix(self.shares).T
        self.currentPrice = np.array( map(lambda x: x[-1], self.price) )
        self.currentValue = np.diag(self.currentPrice) * self.shares
        
    def data(self):
        ret = self.marketValue(self._return(self.price)) * self._weight()
        self.ret = ret
        self.annualRet = ret[-1]**(250/self.days) - 1
        self.risk = np.std(ret)
        self.annualRisk = np.sqrt(250) * self.risk
        return zip(self.marketTime, ret)
        
    def _yahoo(self, symbol, time):
        today = datetime.datetime.today().date().strftime("%Y%m%d")
        #today = "20120428"
        start = time.strftime("%Y%m%d")
        data = ya.get_historical_prices(symbol, start, today)
        return np.sort(data, order='date')
    
    def _return(self, price):
        # FIXME: price may mismatch during Yahoo data updating 
        ret = np.expm1(np.diff(np.log(price)))
        return np.matrix(ret).T
    
    def _weight(self):
        self.start_price  =  np.array ( map(lambda x: x[0], self.price))
        self.start_value  =  np.diag(self.start_price) * self.shares 
        self.weight = self.start_value / np.sum(self.start_value)
        return self.weight
    
    def marketValue(self, ret):
        self.compondRet = np.cumprod(ret+1, axis=0)       
        return self.compondRet
    
    def sharpRatio(self):
        return (self.annualRet - 0.06/365)/self.annualRisk
    
    def covariance(self):
        dailyRet = self._return(self.price).T
        self.Q = np.cov(dailyRet)
        self.invQ = np.linalg.inv(self.Q)
    
    def active(self, expectRet):
        cash = np.sum(self.currentValue)/2
        wt = 0.04
        expectRet = np.matrix(expectRet)
        iota = np.ones_like(expectRet)
        a = expectRet * self.invQ * expectRet.T 
        b = expectRet * self.invQ * iota.T 
        c = iota * self.invQ * iota.T 
        d = a - b*b/c
        weight = np.sqrt(wt)/np.sqrt(d[0,0]) * self.invQ * (expectRet - b[0,0]/c[0,0]*iota).T
        activeRet = expectRet * weight
        cashWeight = cash * weight
        shares = cashWeight.T / self.currentPrice[0:-1]
        return self.symbols, weight, shares, cashWeight, activeRet
    
    def longOnlyPrepare(self):
        params = {"params":"[1.3, 0.7, 0.8, 1.9, 1.2]"}
        self.cloudid = pc.cloud(params)
        return 0
    
    def longOnly(self):
        res = pc.cloud_res(self.cloudid)
        logging.info(res)
        return res
    
def forecast(symbols):
    symbols = map(lambda x: x.strip().upper(), symbols)
    target = np.array (map( lambda x: float(ya.get_year_target(x)) , symbols))
    close  = np.array (map( lambda x: float(ya.get_last_close(x))  , symbols))
    ret    = target / close - 1
    return zip(symbols, close, target, ret)

    
if __name__ == '__main__':
    symbols = ['aapl','xom', 'mcd']
    shares = ['100','100', '200']
    times = ['20120310','20120310','20120310']
    port = portfolio(symbols, shares, times, 1000)
    port.data()
    f = forecast(symbols)
    ret = [d[3] for d in f]
    symbols, actW, actS, actV, actR =  port.active(ret)
    print actW, np.sum(actW.flat)
    