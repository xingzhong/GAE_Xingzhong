#! /usr/bin/env pythonw2.7

import oauth as oauth
import json
import datetime
from google.appengine.api import urlfetch
import logging

class TK:
    def __init__ (self):
        self.OAUTH_TOKEN = '9UkHo7uH6UUfNMrBgY7DVW0yFbiijskbMdZys0ME'
        self.OAUTH_TOKEN_SECRET = 'izHs60ymQgcMfJfCHBAdEaAMPQvnQEnnRdxIQT3J'
        CONSUMER_KEY = 'qUefzctWoJyQ7BQGevKJVQEXMhrqcve4MqlCM3lO'
        CONSUMER_SECRET = 'jNenqr3Ezr9s74YLy1jBVzResnjhJOTCmNBZVYeM'
        self.RESOURCE_URL = 'https://api.tradeking.com/v1'
        ID = 60918935
        
        self.client = oauth.TKClient(CONSUMER_KEY, CONSUMER_SECRET, None)
        
    def request(self, key, type='json', method=urlfetch.GET, params={}):
        url = self.RESOURCE_URL
        for k in key:
            url = "%s/%s"%(url, k)
        url = '%s.%s'%(url, type)
        headers = {}
        req = self.client.make_request(url=url, 
            token=self.OAUTH_TOKEN, secret = self.OAUTH_TOKEN_SECRET,
            additional_params=params, method=method, headers=headers,)
            #protected = True)
        #logging.info("[headers] %s"%req.headers)
        #logging.info("[final_url] %s"%req.final_url)
        #logging.info("[content] %s"%req.content)
        
        return self.decode(req.content)
    
    def decode(self, x):
        #print json.dumps(json.loads(x), indent=2)
        return json.loads(x)
    
    def accounts(self):
        key = ['accounts']
        return self.request(key)
    
    def status(self):
        key = ['utility', 'status']
        return self.request(key)
        
    def version(self):
        key = ['utility', 'version']
        return self.request(key)
        
    def clock(self):
        key = ['market', 'clock']
        res = self.request(key)['response']
        time = res['unixtime']
        status = res['status']['current']
        return datetime.datetime.fromtimestamp(int(time), tz=GMT5()), status
        
    def watch(self):
        key = ['watchlists']
        return self.request(key)
    
    def quote(self, sym):
        key = ['market', 'ext', 'quotes']
        params = {'symbols':sym }
        res = self.request(key, 
            params=params,method=urlfetch.POST)['response']['quotes']['quote']
        chain = {}
        
        for r in res:
            if r is not None:
                key = float(r['strikeprice'])
                chain.setdefault(key, [None, None, None, None])
                if r['put_call'] == 'call':
                    chain[key][0] = float(r['bid']) 
                    chain[key][1] = float(r['ask'])
                if r['put_call'] == 'put':
                    chain[key][2] = float(r['bid'])
                    chain[key][3] = float(r['ask'])
        return chain
    
    def stock(self, sym):
        key = ['market', 'ext', 'quotes']
        params = {'symbols':sym }
        res = self.request(key, params=params)['response']['quotes']['quote']['last']
        return float(res)
    
    def strike(self, sym):
        key = ['market', 'options', 'strikes']
        params = {'symbol':sym }
        res = self.request(key, params=params)['response']['prices']['price']
        return map(float, res)
    
    def expiration(self, sym):
        key = ['market', 'options', 'expirations']
        params = {'symbol':sym }
        res = self.request(key, params=params)
        res = res['response']['expirationdates']['date']
        return map(lambda x:datetime.datetime.strptime(x, "%Y-%m-%d").replace(tzinfo=GMT5()), res)
    
    def options(self, sym):
        key = ['market', 'chains']
        params = {
        'underlying':sym,
        'type':'CALL_AND_PUT',
        'expiration':'ALL',
        'range':'AT_THE_MONEY'
        }
        return self.request(key, params=params)


class GMT5(datetime.tzinfo):
    def __init__(self):
        d = datetime.datetime(datetime.datetime.now().year, 3, 1)
        self.dston = d - datetime.timedelta(days=d.weekday() + 1)
        d = datetime.datetime(datetime.datetime.now().year, 11, 1)
        self.dstoff = d - datetime.timedelta(days=d.weekday() + 1)

    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5) + self.dst(dt)

    def dst(self, dt):
        if self.dston <=  dt.replace(tzinfo=None) < self.dstoff:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(0)
    def tzname(self,dt):
        return "America/New_York"
        
if __name__ == '__main__':
    t = TK()
    res = t.strike('spx,aapl')
    print res