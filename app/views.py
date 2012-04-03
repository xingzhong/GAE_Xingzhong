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
        #add memcache to store 
        #template_values = { 'chain' : chain, 'K':k }
        #template = jinja_environment.get_template('option.html')
        #self.response.out.write(template.render(template_values))
        #start = datetime.datetime.now()
        #r4, r13 = myutils.riskFree()
        #maturity = myutils.maturity(datetime.datetime.now())
        #t1 = myutils.toT(maturity[0] - datetime.datetime.now())
        #t2 = myutils.toT(maturity[1] - datetime.datetime.now())
        #chain1,f1, k1, sigma1, yaTime = myutils.optionChain('^GSPC', maturity[0], t1, r4)
        #end = datetime.datetime.now() - start
        #chain2,f2, k2, sigma2, yaTime = myutils.optionChain('^GSPC', maturity[1], t2, r13)
        #sigma = myutils.average(sigma1, maturity[0],t1, sigma2, maturity[1],t2)
        #vixQuote, vixTime = myutils.vix()
        #end = datetime.datetime.now() - start
        #vixs = db.GqlQuery(" select * from vix ORDER BY gaeTime DESC LIMIT 1" )[0]
        template_values = {
            'author':'Deployed @ Google App Engine', 
            'time':datetime.datetime.now(GMT5()).strftime("%Y-%b-%d %H:%M:%S"),
            'r4': memcache.get("r4"),
            'r13': memcache.get("r13"),
            'near': memcache.get("maturity")[0].strftime("%Y-%b-%d %H:%M:%S"),
            'next': memcache.get("maturity")[1].strftime("%Y-%b-%d %H:%M:%S"),
            'chain1' : memcache.get("chain1"),
            'chain2' : memcache.get("chain2"),
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
        quoteReal, vixTime = myutils.vix()
        maturity = myutils.maturity(start)
        r4, r13 = myutils.riskFree()
        nearTerm = myutils.toT(maturity[0] - start)
        nextTerm = myutils.toT(maturity[1] - start)
        chain1,f1, k1, sigma1, yaTime = myutils.optionChain('^GSPC', 
                maturity[0], nearTerm, r4)
        chain2,f2, k2, sigma2, yaTime = myutils.optionChain('^GSPC', 
                maturity[1], nextTerm, r13)
        quoteModel = myutils.average(sigma1, maturity[0], nearTerm, 
                sigma2, maturity[1],nextTerm)
        costT = (datetime.datetime.now() - start).total_seconds()
        memcache.set_multi({
            "chain1" : chain1,
            "chain2" : chain2,
            "maturity": maturity,
            "nearTerm" : nearTerm,
            "nextTerm" : nextTerm,
            "r4": r4,
            "r13" : r13,
            "quoteReal" : quoteReal,
            "f1" : f1,
            "f2" : f2,
            "k1" : k1,
            "k2" : k2,
            "sigma1": sigma1,
            "sigma2": sigma2,
            "quoteModel": quoteModel,
            "costT" : costT,
            "yaTime" : vixTime })
        data = vix(
            marketTime = vixTime,
            quoteModel = quoteModel,
            quoteReal = quoteReal,
            timeCost = costT,
            riskNear = r4,
            riskNext = r13,
            nearTerm =  nearTerm,
            nextTerm =  nextTerm
            )
        data.put()
        
    