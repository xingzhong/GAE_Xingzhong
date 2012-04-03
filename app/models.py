from google.appengine.ext import db
import datetime

class vix(db.Model):
    gaeTime = db.DateTimeProperty(auto_now_add=True)
    marketTime = db.DateTimeProperty(required=True)
    quoteModel = db.FloatProperty(required=True)
    quoteReal = db.FloatProperty(required=True)
    timeCost = db.FloatProperty(required=True)
    riskNear = db.FloatProperty(required=True)
    riskNext = db.FloatProperty(required=True)
    nearTerm =  db.FloatProperty()
    nextTerm =  db.FloatProperty()
    
