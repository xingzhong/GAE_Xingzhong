import webapp2
import sys
import os
import webapp2
import jinja2
import datetime
import replace as myreplace
import utils as myutils
from models import *


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
        #template_values = { 'chain' : chain, 'K':k }
        #template = jinja_environment.get_template('option.html')
        #self.response.out.write(template.render(template_values))
        start = datetime.datetime.now()
        r4, r13 = myutils.riskFree()
        maturity = myutils.maturity(datetime.datetime.now())
        year = maturity[1].strftime("%Y")
        month1 = maturity[0].strftime("%m")
        day1 = maturity[0].strftime("%d")
        month2 = maturity[1].strftime("%m")
        day2 = maturity[1].strftime("%d")
        t1 = myutils.toT(maturity[0] - datetime.datetime.now())
        t2 = myutils.toT(maturity[1] - datetime.datetime.now())
        chain1,f1, k1, sigma1, yaTime = myutils.optionChain('^GSPC', year, month1, day1, t1, r4)
        chain2,f2, k2, sigma2, yaTime = myutils.optionChain('^GSPC', year, month2, day2, t2, r13)
        sigma = myutils.average(sigma1, maturity[0],t1, sigma2, maturity[1],t2)
        vixQuote, vixTime = myutils.vix()
        end = datetime.datetime.now() - start
        template_values = {
            'author':'Deployed @ Google App Engine', 
            'time':datetime.datetime.now(GMT5()).strftime("%Y-%b-%d %H:%M:%S"),
            'r4': r4,
            'r13': r13,
            'near': maturity[0].strftime("%Y-%b-%d %H:%M:%S"),
            'next': maturity[1].strftime("%Y-%b-%d %H:%M:%S"),
            'chain1' : chain1,
            'chain2' : chain2,
            'k1' : k1, 
            'k2' : k2, 
            'year' : year,
            'month1' : month1,
            'day1' : day1,
            'month2' : month2,
            'day2' : day2,
            'T1' : t1,
            'T2' : t2,
            'f1' : f1,
            'f2' : f2,
            'sigma1' : sigma1,
            'sigma2' : sigma2,
            'sigma' : sigma,
            'loadTime' : end.total_seconds(),
            'vixQuote' : vixQuote,
            'vixTime' : vixTime,
            'yaTime' : yaTime,
            }
        template = jinja_environment.get_template('project.html')
        self.response.out.write(myreplace.replace ( template.render(template_values)))

class JobHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/options')
    