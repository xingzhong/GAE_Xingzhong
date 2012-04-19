import base64
import json
import logging
import urllib
from google.appengine.api import urlfetch


key = 3833
secret_key = 'e70f5b64bc62dc0b206a0c42ad8db0113cb666ac'
base64string = base64.encodestring('%s:%s' % (key, secret_key))[:-1]
http_headers = {'Authorization' : 'Basic %s' % base64string}


def cloud(params):
    logging.info(params)
    params = urllib.urlencode(params)
    response = urlfetch.fetch(url='https://api.picloud.com/r/3677/scipy_qp',
          payload=params, 
          method=urlfetch.POST,
          headers=http_headers)
    data = json.loads(response.content)
    logging.info(data)
    return data['jid']

def cloud_res(jid):
    response = urlfetch.fetch(url='https://api.picloud.com/job/%s/result/'%jid,
          payload={}, 
          method=urlfetch.GET,
          headers=http_headers)
    data = json.loads(response.content)
    #logging.info(data)
    status = str(data.keys()[0])
    if status == 'error':
        logging.info("retry")
        return  cloud_res(jid)
    else:
        return data