#! /usr/bin/env pythonw2.7
import operator
from lxml import etree
import urllib
import numpy as np
from sets import Set
import datetime
import calendar
import tradeking as tk

YEARSECS = 525600*60

def logical_test(x, y):
    """ if x is  nan, y is  nan, return nan
        if x is  nan, y not nan, return y
    """
    if x == None:
        x = np.nan
    if y == None:
        y = np.nan
        
    if np.isnan(x) and np.isnan(y):
        return np.nan
    elif not np.isnan(x):
        return x
    elif not np.isnan(y):
        return y
    else:
        return np.nan


def fromTK(sym, maturity, time, rate):
    """ return tradeking option chain given maturity """
    t = tk.TK()
    res = t.quote('spx,aapl')
    return res

def optionChain(sym, maturity, time, rate):
    call, put = fromYahoo(sym, maturity, time, rate)
    return calculate(call, put, sym, maturity, time, rate)
    
def fromYahoo(sym, maturity, time, rate):
    """ return yahoo option chain given maturity """
    #print "Downloading Data ... "
    year = maturity.strftime("%Y")
    month = maturity.strftime("%m")
    day = maturity.strftime("%d")
    url = "http://finance.yahoo.com/q/op?s=%s&m=%s-%s-%s"%(sym,year,month,day)
    f = urllib.urlopen(url)
    tree = etree.HTML(f.read())
    #print "Parsing"
    yaTime = tree.find(".//span[@class='time_rtq']")
    yaTime = datetime.datetime.strptime(etree.tostring(yaTime, method='text').strip(), "%I:%M%p EDT").time()
    yaDate = datetime.datetime.now().date()
    yaTime = datetime.datetime.combine(yaDate, yaTime)
    table = tree.findall(".//table[@class='yfnc_datamodoutline1']")
    counter = 0
    for t in table:
        items = t[0][0][0]
        data = [text.replace(',','').replace('N/A','nan') 
                for text in items.itertext() if text!=' ']
        data = data[8:]
        Strike = np.array( data[::8], dtype=float)
        Last = np.array (data[2::8], dtype=float)
        Bid = np.array (data[4::8], dtype=float)
        Ask = np.array (data[5::8], dtype=float)
        if counter == 0 : # call options
            callSpread = map(None, Bid, Ask, [], [])
            call = dict(zip(Strike, callSpread))
        else :  # put options
            putSpread = map(None, [], [], Bid, Ask)
            put = dict(zip(Strike, putSpread))
        counter = counter + 1

    #print "Finish Parsing"

def calculate(call, put, sym, maturity, time, rate):
    keys = Set(call.keys() + put.keys())
    Nones = ( np.nan, np.nan, np.nan, np.nan)
            
    chain = [ (k, map(logical_test, call.get(k, Nones), put.get(k, Nones)) )
            for k in keys ]
    
    chain = [ (c[0], c[1][0], c[1][1], c[1][2], c[1][3], np.nan) for c in chain ]
    #chain = np.core.records.array(chain, names='strk, callBid, callAsk, putBid, putAsk')
    chain = np.array(chain, dtype=[
        ('strk',np.float),
        ('callBid',np.float),
        ('callAsk',np.float),
        ('putBid',np.float),
        ('putAsk',np.float),
        ('price',np.float),
        ])
    chain = np.sort(chain, order='strk')

    kmin = abs ( chain['callBid'] + chain['callAsk'] - chain['putBid'] - chain['putAsk'] )

    index = np.nanargmin(kmin)
    strk = chain[index]['strk']
    smallest = 0.5 * (chain[index]['callBid'] + chain[index]['callAsk'] - 
            chain[index]['putBid'] - chain[index]['putAsk'])
    expe = np.exp(rate/100 * time)
    F = strk + expe * smallest
    
    k = chain[chain['strk']<F][-1]['strk']
    indk = np.argwhere (chain['strk'] == k)[0][0]
    chain[indk]['price'] = 0.25 * (chain[index]['callBid'] + chain[index]['callAsk'] + 
            chain[index]['putBid'] + chain[index]['putAsk'])
    
    # print k
    # select out of money put < k
    
    
    call = np.extract(chain['strk']>k, chain)
    put = np.extract(chain['strk']<k, chain)[::-1]
    for p in findConValue(put['putBid'], np.nan, put):
        price = 0.5 * ( p['putBid'] + p['putAsk'] )
        index = np.argwhere( chain['strk'] == p['strk'])[0][0]
        chain[index]['price'] = price
     
    # select out of money call > k    
    for c in findConValue(call['callBid'], np.nan, call):
        price = 0.5 * ( c['callBid'] + c['callAsk'] )
        index = np.argwhere( chain['strk'] == c['strk'])[0][0]
        chain[index]['price'] = price 
    
    chain = chain[ np.isnan(chain['price']) == False ]
    dk = np.convolve(chain['strk'], [0.5, 0, -0.5], 'same')
    dk[0] = chain['strk'][1] - chain['strk'][0]
    dk[-1] = chain['strk'][-1] - chain['strk'][-2]
    #print len(dk), len(chain['strk'])
    
    
    for i in range(len(chain)):
        chain[i]['price'] = dk[i]/(chain[i]['strk']**2) * expe * chain[i]['price']
    
    sigma = 2 / time * np.sum(chain['price']) - 1/time * (F/k -1)**2
        
    return chain, F, float(k), float(sigma), yaTime

def dictSort(x):
    """Sort a dict by value"""
    return sorted(x.iteritems(), key=operator.itemgetter(1))

def findConValue(x, v, X):
    """Find the first happen that two consecutive v in x,
        and return the list before it happens.
    """
    y = zip(x, x[1:])
    res = map ( lambda x : np.isnan(x[0]) and np.isnan(x[1]) , y )
    if True in res:
        return X[:res.index(True)]
    else:
        return X

def riskFree():
    url = "http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Datasets/daily_treas_bill_rates.xml"
    f = urllib.urlopen(url)
    xml = etree.parse(f)
    xml = xml.findall(".//G_INDEX_DATE")[-1]
    r4 = xml.find(".//ROUND_B1_CLOSE_4WK_2")
    r4 = float(etree.tostring(r4, method='text'))
    r13 = xml.find(".//ROUND_B1_CLOSE_13WK_2")
    r13 = float( etree.tostring(r13, method='text'))
    return r4, r13
    
def settledDay(date):
    month = date.month
    year = date.year
    c = calendar.TextCalendar()
    result = []
    for y in [year, year+1]:
        for m in range(month, 12):
            counter = 3
            for d in c.itermonthdays2(y, m):
                if d[0] != 0 and d[1] == calendar.FRIDAY:
                    counter = counter - 1;
                    if counter == 0:
                        settle = datetime.datetime(y, m, d[0], 8, 30)
                        if settle > date :
                            result.append(settle)
    return result

def maturity(date):
    return settledDay(date)[:2]

def toT(x):
    return x.total_seconds()/YEARSECS

def average(s1, t1, dt1, s2, t2, dt2):
    now = datetime.datetime.now()
    Nt1 = (t1-now).total_seconds() / 60
    Nt2 = (t2-now).total_seconds() / 60
    N30 = 43200
    N365 = 525600
    return float(100 * np.sqrt( N365/N30*( dt1*s1*(Nt2-N30)/(Nt2-Nt1) + dt2*s2*(N30-Nt1)/(Nt2-Nt1) )))

def vix():
    url = "http://finance.yahoo.com/q/op?s=^vix"
    f = urllib.urlopen(url)
    tree = etree.HTML(f.read())
    quote = tree.find(".//span[@class='time_rtq_ticker']")
    time = tree.find(".//span[@class='time_rtq']")
    quote = float( etree.tostring(quote, method='text') )
    time = datetime.datetime.strptime(etree.tostring(time, method='text').strip(), "%I:%M%p EDT").time()
    date = datetime.datetime.now().date()
    now = datetime.datetime.combine(date, time)
    return quote , now
    
if __name__ == '__main__':
    #print vix()
    optionChain('^GSPC', '2012', '05', '18', 0.125347883345, 0.07)
    #riskFree()
    #now = datetime.datetime.today()
    #date = maturity(now)
    #average (0.1, date[0], 0.024 , 0.2, date[1], 0.101)
