#!/usr/bin/env pythonw2.7

import webapp2

from app.views import *
        
app = webapp2.WSGIApplication([
    ('/', MainHandler), 
    ('/options', OptionHandler),
    ('/job', JobHandler)
    ], debug=True)