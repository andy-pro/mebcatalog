import fnmatch
#import os
from mebcatalog import render_404, mebcatalog

def admin(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['Admin:']

def index(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['Index file:']

def application(environ, start_response):
    routes = [('admin*',      admin),
              ('',            mebcatalog),
              ('index',       index),
              ('mebcatalog*', mebcatalog),]
    #os.chdir(os.path.dirname(__file__))    # for I/O operations with files in wsgi directory, base.html, for example 
    path = (environ['PATH_INFO']).strip('/')
    #print >> environ['wsgi.errors'], "wsgi routes application debug"
    for pathmask, app in routes:
        if fnmatch.fnmatch(path, pathmask):
            return app(environ, start_response)
    #environ['ExpectedPath'] = pathmask
    return render_404(environ, start_response)


#from paste.exceptions.errormiddleware import ErrorMiddleware
#application = ErrorMiddleware(application, debug=True)
#------------------------Extended debug information-------------------------------------------------
#from paste.evalexception.middleware import EvalException
#application = EvalException(application)