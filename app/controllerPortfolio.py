#!/usr/bin/env pythonw2.7
import datetime
import yahoo as ya
import numpy as np

class portfolio:
    def __init__(self, symbols, shares, times):
        self.symbols = map(lambda x: x.strip().capitalize(), symbols)
        self.shares  = map(int, shares)
        self.times   = map(lambda x: datetime.datetime.strptime(x, "%Y%m%d").date(), times)
        
    def data(self):
        start = min(self.times)
        price = map(lambda x: self._yahoo(x, start)['adj'], self.symbols)
        shares = np.matrix(self.shares).T
        return self._return(price) * shares
        
    def _yahoo(self, symbol, time):
        today = datetime.datetime.today().date().strftime("%Y%m%d")
        start = time.strftime("%Y%m%d")
        return ya.get_historical_prices(symbol, start, today)
    
    def _return(self, price):
        ret = np.exp(np.diff(np.log(price))) - 1
        return np.matrix(ret).T
        

if __name__ == '__main__':
    symbols = ['aapl', 'ba', 'c']
    shares = ['100', '200', '300']
    times = ['20120212', '20120212', '20120212']
    port = portfolio(symbols, shares, times)
    print port.data()