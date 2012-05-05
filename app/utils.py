#! /usr/bin/env pythonw2.7
import operator
from lxml import etree
import urllib
import numpy as np
from sets import Set
import datetime
import calendar
import tradeking as tk
import logging
from google.appengine.api import memcache
from models import *

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


def makeSymbol(sym, term, strikes):
    clists = map(lambda x: "%s%sC%08u"%(sym, term.strftime("%y%m%d"), 1000*x), 
        strikes)
    plists = map(lambda x: "%s%sP%08u"%(sym, term.strftime("%y%m%d"), 1000*x), 
        strikes)
    clists.extend(plists)
    #logging.info(clists)
    return ','.join(clists)

def fromTK(sym):
    """ return tradeking option chain given maturity """
    start = datetime.datetime.now()
    logging.info("[start]%s"%start)
    t = tk.TK()
    
    now, status = t.clock()
    memcache.set("now", now)
    logging.info(status)
    
    nearRate = memcache.get("nearRate")
    nextRate = memcache.get("nextRate")
    logging.info("memcache [nearRate nextRate]%s %s"%(nearRate, nextRate))
    if (nearRate and nextRate) is None:
        nearRate, nextRate = riskFree()
        if not memcache.set("nearRate", nearRate, 3600*12):
            logging.error("nearRate memcache set failed")
        if not memcache.set("nextRate", nextRate, 3600*12):
            logging.error("nextRate memcache set failed")
        logging.info("Downloading [nearRate nextRate]%s %s"%(nearRate, nextRate))
    
    # get the near and next term options expiration date
    near = memcache.get("near")
    next = memcache.get("next")
    logging.info("memcache [now near next]%s %s %s"%(now, near, next))
    if ( near and next ) is None:
        expirations = t.expiration(sym)
        near = expirations[0]
        next = expirations[1]
        if not memcache.set("near", near, 3600*12):
            logging.error("near memcache set failed")
        if not memcache.set("next", next, 3600*12):
            logging.error("next memcache set failed")
        logging.info("Downloading [near next]%s %s"%(near, next))
        
    # get the available strike prices 
    strikes = memcache.get("strikes")
    logging.info("memcache strikes")
    if strikes is None:
        strikes = t.strike(sym) 
        if not memcache.set("strikes", strikes, 3600*12):
            logging.error("strikes memcache set failed")
        logging.info("Downloading strikes")
    
    # calulate normalized time 
    
    nearT, nearD = toT(near - now)
    nextT, nextD = toT(next - now)
    
    memcache.set("nearT", nearT)
    memcache.set("nextT", nextT)
    logging.info("[nearT nearD]%s %s"%(nearT, nearD))
    logging.info("[nextT nextD]%s %s"%(nextT, nextD))
    
    # generate symbol lists to query 
    nearOps = memcache.get("nearOps")
    nextOps = memcache.get("nextOps")
    logging.info("memcache nearOps & nextOps")
    if (nearOps and nextOps) is None:
        nearOps = makeSymbol(sym, near, strikes)
        nextOps = makeSymbol(sym, next, strikes)
        if not memcache.set("nearOps", nearOps, 3600*12):
            logging.error("nearOps memcache set failed")
        if not memcache.set("nextOps", nextOps, 3600*12):
            logging.error("nextOps memcache set failed")
        logging.info("generate symbol lists")
    
    if status != 'open' : 
        return memcache.get("quote")
    
    # cache the data
    nearChain = t.quote(nearOps)
    logging.info("cache nearChain")
    
    
    # calculate the sigma 
    nearChain, nearF, nearK, nearSigma, nearPSigma, nearCSigma = getSigma(
            nearChain, nearRate, nearT)
    memcache.set_multi(
        {
            'nearChain' : nearChain,
            'nearF' : nearF, 
            'nearK' : nearK, 
            'nearSigma' : nearSigma,
            'nearPSigma' : nearPSigma,
            'nearCSigma' : nearCSigma,
        }
        )
    logging.info("[nearSigma]%s"%(nearSigma))
    
    nextChain = t.quote(nextOps)
    logging.info("cache nextChain")
    nextChain, nextF, nextK, nextSigma, nearPSigma, nearCSigma = getSigma(
            nextChain, nextRate, nextT)
    memcache.set_multi(
        {
            'nextChain' : nextChain,
            'nextF' : nextF, 
            'nextK' : nextK, 
            'nextSigma' : nextSigma,
            'nextPSigma' : nearPSigma,
            'nextCSigma' : nearCSigma,
        }
        )
    logging.info("[nextSigma]%s"%(nextSigma))
    
    
    N30 = 43200
    N365 = 525600
    quote = float(100 * np.sqrt( N365/N30*( 
            nearT*nearSigma*(nextD-N30)/(nextD-nearD) + 
            nextT*nextSigma*(N30-nearD)/(nextD-nearD) )))
            
    memcache.set("quote", quote)
    
    real = t.stock('vix')
    memcache.set("real", real)
    
    # store to db
    costT = (datetime.datetime.now() - start).total_seconds()
    memcache.set("costT", costT)
    logging.info("[costT]%s"%costT)
    
    data = vix(
        marketTime = now,
        quoteModel = quote,
        quoteReal = real,
        timeCost = costT,
        riskNear = nearRate,
        riskNext = nextRate,
        nearTerm =  nearT,
        nextTerm =  nextT,
        )
    data.put()
    
    return quote
    

def getSigma(chain, rate, time):
    # rate is risk-free rate
    # chain is a dict
    # time is time to maturity (e.g. 0.004)
    chain = [ (c[0], c[1][0], c[1][1], c[1][2], c[1][3], np.nan, np.nan) for c in chain.iteritems() ]
    chain = np.array(chain, dtype=[
        ('strk',np.float),
        ('callBid',np.float),
        ('callAsk',np.float),
        ('putBid',np.float),
        ('putAsk',np.float),
        ('price',np.float),
        ('contr',np.float),
        ])
    chain = np.sort(chain, order='strk')
    logging.info("Finish numpy array ")
    
    kmin = abs ( chain['callBid'] + chain['callAsk'] - chain['putBid'] - chain['putAsk'] )
    index = np.nanargmin(kmin)
    strk = chain[index]['strk']
    logging.info("[Locate Strk]%s"%strk)
    smallest = 0.5 * (chain[index]['callBid'] + chain[index]['callAsk'] - 
            chain[index]['putBid'] - chain[index]['putAsk'])
    expe = np.exp(rate/100 * time)
    F = strk + expe * smallest    
    logging.info("[Locate F]%s"%F)
    
    
    k = chain[chain['strk']<F][-1]['strk']
    indk = np.argwhere (chain['strk'] == k)[0][0]
    chain[indk]['price'] = 0.25 * (chain[index]['callBid'] + chain[index]['callAsk'] + 
            chain[index]['putBid'] + chain[index]['putAsk'])

    # select out of money put < k    
    call = np.extract(chain['strk']>k, chain)
    put = np.extract(chain['strk']<k, chain)[::-1]
    for p in findConValue(put['putBid'], put):
        price = 0.5 * ( p['putBid'] + p['putAsk'] )
        index = np.argwhere( chain['strk'] == p['strk'])[0][0]
        chain[index]['price'] = price
     
    # select out of money call > k    
    for c in findConValue(call['callBid'], call):
        price = 0.5 * ( c['callBid'] + c['callAsk'] )
        index = np.argwhere( chain['strk'] == c['strk'])[0][0]
        chain[index]['price'] = price 
    
    chain = chain[ np.isnan(chain['price']) == False ]
    
    logging.info("scalable numpy array ")
    dk = np.convolve(chain['strk'], [0.5, 0, -0.5], 'same')
    dk[0] = chain['strk'][1] - chain['strk'][0]
    dk[-1] = chain['strk'][-1] - chain['strk'][-2]

    for i in range(len(chain)):
        chain[i]['contr'] = dk[i]/(chain[i]['strk']**2) * expe * chain[i]['price']
    logging.info("finish contributation calculate ")
    
    sigma = 2 / time * np.cumsum(chain['contr']) - 1/time * (F/k -1)**2
    chain['contr']  =  sigma
    
    indk = np.argwhere (chain['strk'] == k)[0][0]
    putSigma = sigma[indk-1]
    callSigma = sigma[-1]-sigma[indk+1]
    logging.info("[put  sigma] = %s"%putSigma)
    logging.info("[call sigma] = %s"%callSigma)
    
    sigma = sigma[-1]
    return chain, F, float(k), float(sigma), float(putSigma), float(callSigma)

def optionChain(sym, maturity, time, rate):
    call, put, yaTime = fromYahoo(sym, maturity, time, rate)
    return calculate(call, put, sym, maturity, time, rate, yaTime)
    
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
    try:
        yaTime = datetime.datetime.strptime(etree.tostring(yaTime, method='text').strip(), "%I:%M%p EDT").time()
    except ValueError:
        yaTime = datetime.datetime.strptime(etree.tostring(yaTime, method='text').strip(), "%b %d").time()
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
    return call , put, yaTime
    #print "Finish Parsing"

def calculate(call, put, sym, maturity, time, rate, yaTime):
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
    
    if np.isnan(index):
        return chain, -1, float(-1), float(-1), yaTime
        
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

def findConValue(x, X):
    """Find the first happen that two consecutive v in x,
        and return the list before it happens.
    """
    y = zip(x, x[1:])
    res = map ( lambda x : x[0]==0.0 and x[1]==0.0 , y )
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
    t = x.total_seconds()/YEARSECS
    dt = x.total_seconds()/60
    return t, dt

def average(s1, t1, dt1, s2, t2, dt2, now=datetime.datetime.now()):
    Nt1 = (t1-now).total_seconds() / 60
    Nt2 = (t2-now).total_seconds() / 60
    N30 = 43200
    N365 = 525600
    return float(100 * np.sqrt( N365/N30*( dt1*s1*(Nt2-N30)/(Nt2-Nt1) + dt2*s2*(N30-Nt1)/(Nt2-Nt1) )))

def update_vix():
    url = "http://finance.yahoo.com/q/op?s=^vix"
    f = urllib.urlopen(url)
    tree = etree.HTML(f.read())
    quote = tree.find(".//span[@class='time_rtq_ticker']")
    timeS = tree.find(".//span[@class='time_rtq']")
    quote = float( etree.tostring(quote, method='text') )
    try:
        time = datetime.datetime.strptime(etree.tostring(timeS, method='text').strip(), "%I:%M%p EDT").time()
    except ValueError:
        time = datetime.datetime.strptime(etree.tostring(timeS, method='text').strip(), "%b %d").time()
    date = datetime.datetime.now().date()
    now = datetime.datetime.combine(date, time)
    return quote , now

def quote(sym):
    t = tk.TK()
    #expirations = t.expiration(sym)
    #near = expirations[1]
    underline = t.quote_1(sym)
    #strikes = t.strike(sym)
    #nearOps = makeSymbol(sym, near, strikes)
    #Ops = nearOps.split(',')
    #chains = t.quote_1(Ops[80])
    return underline

def cache(sym):
    for s in sym:
        full = quote(s)
        store = intraday(
            timestamp = datetime.datetime.fromtimestamp(int(full['timestamp'])),
            quote = float(full['last']),
            symbol = full['symbol'])
        store.put()

def status():
    t = tk.TK()
    return t.clock()



if __name__ == '__main__':
    #print vix()
    optionChain('^GSPC', '2012', '05', '18', 0.125347883345, 0.07)
    #riskFree()
    #now = datetime.datetime.today()
    #date = maturity(now)
    #average (0.1, date[0], 0.024 , 0.2, date[1], 0.101)
