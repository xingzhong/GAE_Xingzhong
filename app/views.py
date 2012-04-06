import webapp2
import sys
import os
import webapp2
from google.appengine.api import memcache
import jinja2
import datetime
import replace as myreplace
import utils as myutils
from models import *
import logging
import constant as cst


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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/../templates/')
)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'author':'Deployed @ Google App Engine', 
            'time':datetime.datetime.now(GMT5()).strftime("%Y-%b-%d %H:%M:%S")
            }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(myreplace.replace ( template.render(template_values)))

class OptionHandler(webapp2.RequestHandler):
    def get(self):
        vixs = memcache.get("vixs")
        if vixs is None:
            vixs = db.GqlQuery(" select * from vix ORDER BY marketTime DESC LIMIT 100" )
            if not memcache.add("vixs", vixs, 10):
                logging.error("vixs memcache set failed")
        maturity = memcache.get("maturity")
        near = None
        next = None
        if maturity:
            near = maturity[0].strftime("%Y-%b-%d %H:%M:%S")
            next = maturity[1].strftime("%Y-%b-%d %H:%M:%S")
        try:
            iter(memcache.get("chain1"))
        except TypeError:
            chain1 = []
        else:
            chain1 = memcache.get("chain2")
        try:
            iter(memcache.get("chain2"))
        except TypeError:
            chain2 = []
        else:
            chain2 = memcache.get("chain2")
        template_values = {
            'author':'Deployed @ Google App Engine', 
            'time':datetime.datetime.now(GMT5()).strftime("%Y-%b-%d %H:%M:%S"),
            'r4': memcache.get("r4"),
            'r13': memcache.get("r13"),
            'near': near,
            'next': next,
            'chain1' : chain1,
            'chain2' : chain2,
            'k1' : memcache.get("k1"), 
            'k2' : memcache.get("k2"), 
            'T1' : memcache.get("nearTerm"),
            'T2' : memcache.get("nextTerm"),
            'f1' : memcache.get("f1"),
            'f2' : memcache.get("f2"),
            'sigma1' : memcache.get("sigma1"),
            'sigma2' : memcache.get("sigma2"),
            'quoteModel' : memcache.get("quoteModel"),
            'loadTime' : memcache.get("costT"),
            'vixQuote' : memcache.get("quoteReal"),
            'yaTime' : memcache.get("yaTime"),
            'vixs': vixs,
            }
        template = jinja_environment.get_template('project.html')
        self.response.out.write(myreplace.replace ( template.render(template_values)))

class JobHandler(webapp2.RequestHandler):
    def get(self):
        #add memcache to store 
        start = datetime.datetime.now()
        if start.weekday() in [6,7]:
            logging.info("Not workday, just return")
            return None
        logging.info("Workday, continue")
        quote = myutils.fromTK('SPX')
        logging.info("update vix %s"%quote)
        
class TKHandler(webapp2.RequestHandler):   
    def get(self):
        template = jinja_environment.get_template('trade.html')
        template_values = {
            'head' : cst.head,
            'nearRate' : memcache.get("nearRate"),
            'nextRate' : memcache.get("nextRate"),
            'near' : memcache.get("near"),
            'next' : memcache.get("next"),
            'nearT' : memcache.get("nearT"),
            'nextT' : memcache.get("nextT"),
            'now' : memcache.get("now"),
            'nearOps' : memcache.get("nearOps"),
            'nextOps' : memcache.get("nextOps"),
            'nearChain' : memcache.get("nearChain"),
            'nearF' : memcache.get("nearF"), 
            'nearK' : memcache.get("nearK"), 
            'nearSigma' : memcache.get("nearSigma"),
            'nearPSigma' : memcache.get("nearPSigma"),
            'nearCSigma' : memcache.get("nearCSigma"),
            'nextChain' : memcache.get("nextChain"),
            'nextF' : memcache.get("nextF"), 
            'nextK' : memcache.get("nextK"), 
            'nextSigma' : memcache.get("nextSigma"),
            'nextPSigma' : memcache.get("nextPSigma"),
            'nextCSigma' : memcache.get("nextCSigma"),
            'quote' : memcache.get("quote"), 
            'real' : memcache.get("real"),
            'costT' : memcache.get("costT"),
        }
        self.response.out.write(myreplace.replace ( template.render(template_values)))
        
class DrawHandler(webapp2.RequestHandler):   
    def get(self):
        limit = int( self.request.GET['limit'] )
        logging.info(limit)
        data = vix.all()
        data.order("-marketTime")
        vixs = data.fetch(limit)
        template = jinja_environment.get_template('draw.html')
        template_values = {
            'head' : cst.head,
            'vixs' : vixs,
            'limit': limit,
        }
        self.response.out.write(template.render(template_values))