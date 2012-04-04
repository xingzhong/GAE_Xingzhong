#! /usr/bin/env pythonw2.7

import oauth as oauth
import json

class TK:
    def __init__ (self):
        self.OAUTH_TOKEN = '9UkHo7uH6UUfNMrBgY7DVW0yFbiijskbMdZys0ME'
        self.OAUTH_TOKEN_SECRET = 'izHs60ymQgcMfJfCHBAdEaAMPQvnQEnnRdxIQT3J'
        CONSUMER_KEY = 'qUefzctWoJyQ7BQGevKJVQEXMhrqcve4MqlCM3lO'
        CONSUMER_SECRET = 'jNenqr3Ezr9s74YLy1jBVzResnjhJOTCmNBZVYeM'
        self.RESOURCE_URL = 'https://api.tradeking.com/v1'
        ID = 60918935
        
        self.client = oauth.TKClient(CONSUMER_KEY, CONSUMER_SECRET, None)
        
    def request(self, key, type='json', method='GET', params={}):
        url = self.RESOURCE_URL
        for k in key:
            url = "%s/%s"%(url, k)
        url = '%s.%s'%(url, type)
        req = self.client.make_request(url=url, 
            token=self.OAUTH_TOKEN, secret = self.OAUTH_TOKEN_SECRET,
            additional_params=params)
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
        return self.request(key)
        
    def watch(self):
        key = ['watchlists']
        return self.request(key)
    
    def quote(self, sym):
        key = ['market', 'ext', 'quotes']
        
        params = {'symbols':sym }
        return self.request(key, params=params)
    
    def options(self, sym):
        key = ['market', 'chains']
        params = {
        'underlying':sym,
        'type':'CALL_AND_PUT',
        'expiration':'ALL',
        'range':'AT_THE_MONEY'
        }
        return self.request(key, params=params)

if __name__ == '__main__':
    t = TK()
    res = t.quote('spx,aapl')
    print res