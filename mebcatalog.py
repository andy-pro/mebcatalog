﻿# -*- coding: utf-8 -*-
#import fnmatch
from string import Template
#from pprint import pprint
import os, sys, glob, re
import basetypes
import urllib
#from basetypes import titles
prjroot = r'c:\_projects'

class PercentTemplate(Template):
    delimiter = '%'
    
def base_dict(icat):
    k = len(basetypes.titles)
    cats = ','.join(("'%s'" % (item) for item in basetypes.titles))
    href = ','.join(("'?cat=%s'" % (item) for item in xrange(k)))
    basedict = { 'arraycat': cats, 'arrayhrefmenu': href, 'show_photo': 'false' }    
    basedict['prjpath'] = ''
    if icat < 0:
        basedict['header'] = 'Каталог мебели'
        basedict['arrayhint'] = cats
        basedict['arraytitle'] = cats
        basedict['arrayhrefimg'] = href
        basedict['arrayimg'] = ','.join(("'_homeimages/%s'" % (item) for item in basetypes.catfiles))  
    else:
        basedict['header'] = ''
        basedict['arrayhint'] = ''
        basedict['arraytitle'] = ''
        basedict['arrayhrefimg'] = ''
        basedict['arrayimg'] = ''    
    return basedict    
    
def send_template(environ, start_response, dict):
    os.chdir(os.path.dirname(__file__))    # for I/O operations with files in wsgi directory, base.html, for example 
    filein = open( 'base.html' )
    src = PercentTemplate( filein.read() )
    start_response('200 OK', [('content-type','text/html; charset=utf-8')])
    return [src.substitute(dict)]
               
def view_main_page(environ, start_response):
    basedict = base_dict(-1)
    return send_template(environ, start_response, basedict)
    
def view_category_page(environ, start_response):
    icat = int(environ['cat_arg'])
    basedict = base_dict(icat)
    basedict['header'] = basetypes.titles[icat]
    mebcatu = basetypes.mebcatu[icat]
    mymask = os.sep + mebcatu + '*'
    count = 1
    arrayhrefimg = []
    arrayimg = []
    for myclient in os.listdir(prjroot):
        myclientfull = os.path.join(prjroot, myclient)
        if os.path.isdir(myclientfull):
            s = unicode(myclientfull, 'cp1251') + mymask
            for myproject in glob.glob(s):
                if os.path.isdir(myproject):
                    thumbnails = glob.glob(myproject + basetypes.mymasktb) # list of all thumbnails *.jpg in project dir
                    lentb = len(thumbnails)
                    if lentb:
                        itb = 0
                        for tb in thumbnails:
                            parts = os.path.split(tb)      # разделение пути
                            s = parts[1]	# filename
                            if s[0] == '_':
                                break
                            itb += 1
                        if itb >= lentb:
                            itb = 0
                        parts = re.split(r'[\\/]', thumbnails[itb])
                        tbfile = os.path.join(*parts[2:])
                        s = tbfile.replace('\\', '/')
                        arrayimg.append(s.encode('utf-8'))
                        tbfile = os.path.join(*parts[2:4])
                        s = tbfile.replace('\\', '/')                       
                        arrayhrefimg.append('?cat=%s&dir=%s' % (icat, s.encode('utf-8')))
                        strcount = str(count)
                        mebcatcnt = mebcatu + ' ' + strcount
                        basedict['arraytitle'] = basedict['arraytitle'] + "'%s'," % (mebcatcnt.encode('utf-8'))
                        s = unicode(myclient, 'cp1251')
                        basedict['arrayhint'] = basedict['arrayhint'] + "'%s'," % (s.encode('utf-8'))
                        count += 1
    
    basedict['arrayhrefimg'] = ','.join(["'%s'" % (item) for item in arrayhrefimg])    
    basedict['arrayimg'] = ','.join(["'%s'" % (item) for item in arrayimg])
    return send_template(environ, start_response, basedict)

def view_project_page(environ, start_response):
    icat = int(environ['cat_arg'])
    basedict = base_dict(icat)
    dirname = urllib.unquote(environ['dir_arg'])
    prjpath = dirname.decode('utf-8')
    s = os.path.join(prjroot, prjpath) + basetypes.mymasktb
    thumbnails = glob.glob(s)
    lentb = len(thumbnails)
    #print >> environ['wsgi.errors'], lentb
    if lentb:        
        basedict['header'] = dirname
        basedict['prjpath'] = dirname
        itb = 1
        arrayimg = []
        arrayhrefimg = []
        hintvalue = ''
        for tb in thumbnails:
            filename = os.path.split(tb)            
            tbfile = '/'.join(['/thumbnails', filename[1]])   # tbfile = os.path.join('thumbnails', filename[1]); tbfile = tbfile.replace('\\', '/')
            arrayimg.append(tbfile.encode('utf-8'))
            tbfile = '/'.join(['/images', filename[1]])
            arrayhrefimg.append(tbfile.encode('utf-8'))
            #basedict['arrayhint'] = basedict['arrayhint'] + "'Фото %d'," % (itb)
            hintvalue = hintvalue + "'Фото %d'," % (itb)
            itb += 1
        basedict['arrayhrefimg'] = ','.join(("'%s'" % (item) for item in arrayhrefimg))    
        basedict['arrayimg'] = ','.join(("'%s'" % (item) for item in arrayimg))
        basedict['arrayhint'] = hintvalue
        basedict['arraytitle'] = hintvalue
        basedict['show_photo'] = 'true'
    return send_template(environ, start_response, basedict)
    
def mebcatalog(environ, start_response):
    query = environ['QUERY_STRING'].strip('/')    
    querynames = ['cat', 'dir', 'file']
    args = query.split('&')
    check = 0
    if len(args) > 0:
        for arg in args:
            value = arg.split('=')
            if value[0] in querynames:
                environ[value[0]+'_arg'] = value[1]    # add new keys to environ dict: cat, dir, file
                check += 1
    #print >> environ['wsgi.errors'], 'query:%s, check:%s' % (query, check)
    if check == 0:
        return view_main_page(environ, start_response)
#--------------no check arg "cat_arg"-----------------------------------------------------------
    # elif check == 1:
        # return view_category_page(environ, start_response)
    # elif check == 2:
        # return view_project_page(environ, start_response)
    # else:
        # return render_404(environ, start_response)      
#--------------for error detection-----------------------------------------------------------
    try:
        icat = int(environ['cat_arg'])
        icat = icat
        if icat > 7 or icat < 0:
            raise Exception ('Catalog out of range')
        elif check == 1: return view_category_page(environ, start_response)
        elif check == 2: return view_project_page(environ, start_response)
        else: raise Exception ('URL is invalid')
    except Exception as message:
        #print >> environ['wsgi.errors'], message
        return render_404(environ, start_response)
        #return view_main_page(environ, start_response)
#-------------------------------------------------------------------------        
def render_404(environ, start_response):
    # start_response('404 Not Found', [('Content-type', 'text/plain')])
    # ret = ['404 Not Found\n']    
    # ret.extend(["%s: %s\n" % (key, value) for key, value in environ.iteritems()])
    # ret.extend(["%s\n" % (value) for value in sys.path])
    # ret.append('Current working directory = %s\n' % (os.getcwd()))
    # ret.append('mod_wsgi.SCRIPT_FILENAME: = %s\n' % (environ['SCRIPT_FILENAME']))
    # ret.append('__file__: = %s\n' % (os.path.dirname(__file__)))
    # return ret
    start_response('404 Not Found', [('content-type','text/html')])
    return ["""<html><h1>404 Not Found</h1><p>That page is unknown.
Return to the <a href="/">home page</a></p></html>"""]
#-------------------------------------------------------------------------        
