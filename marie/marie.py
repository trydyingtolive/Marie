""" Marie: a WSGI micro-framework for websites in Python
    Copyright (C) 2010-2011 Mark W. Lee

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import cgi
import urlparse
import Cookie
import time
import inspect
import hashlib
import logging
import traceback
from cProfile import Profile
from wsgiref.simple_server import make_server

try:
    from redis import Redis
except:
    Redis=None
    
try:
    import json
except:
    try:
        import simplejson as json
    except:
        json=None

try:
    from mako.lookup import TemplateLookup
    from mako import exceptions as mako_exceptions
    lookup = TemplateLookup() ##Initialize Mako lookup object
except:
    pass

__version__ = '1.0.3'



##User defined properites and defaults
content_type='text/html' ## Change to 'application/xhtml+xml' for xhtml
encoding = 'utf-8'
error_file = None ##File location of error log or None
salt = 'mariesalt' ## Salt for authorization
secure_cookie=False ##Send session information via Secure Cookies
session_lease=60*60*24 ##TTL for sessions
user_db=0 ##Redis database for storing users
registration_db=1 ##Redis database for storing registrations
session_db=2 ##Redis database for storing sessions
template_dirs = ['.'] ##List of directories of templates
template_bytecode_dir = None ##Location of temporary bytecode dir
template_updates = True ##Checks to see if newer versions of the templates exist

##Default Scripts:
def error_script():
    "Default message for errors"
    return '<h2>Error:</h2>\
            A serious error was returned and has been logged.'

def page_not_found():
    "Default message for 404s"
    return """<h2>Page Not Found</h2>
We are sorry but the document you requested could not be located.
"""

mako_lookup_obj=None

## Errors and Logging
def log(error):
    if error_file:
        logger = logging.getLogger('MarieWSGI')
        hdl = logging.FileHandler(error_file)
        fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdl.setFormatter(fmt)
        logger.addHandler(hdl)
        logger.exception(error)

class RerouteError(Exception):
    "Used for catching reroutes to internal routes"
    pass


class application:
    "The WSGI Application yields output according to PEP333"
    auth_routes={}
    unauth_routes={}
    internal_routes={}

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response
        self.response=None
        self.status=None
        self.choose_function()

    def choose_function(self):
        self.environ['MARIE_HEADERS']=HTTP_Headers()
        self.environ['MARIE_STATUS']='200 OK'
        self.environ['MARIE_COOKIES']=self.set_cookies()
        auth=self.check_auth()
        method = self.environ['REQUEST_METHOD']
        path = self.get_path()
        self.environ['MARIE_QRS']=Qrs(self.environ)
        self.environ['MARIE_BODY']=Body(self.environ)
        route_function = self.get_route(auth,method,path)
        self.run_function(route_function)

    def run_function(self, route_function):
        args = self.get_args(route_function)
        template = route_function['template']
        try:
            self.output = route_function['function'](*args)
            if template:
                lookup.directories=template_dirs
                lookup.output_encoding=encoding
                lookup.filesystem_checks=template_updates
                try:
                    tp_obj = lookup.get_template(template)
                    self.output=tp_obj.render(**self.output)
                except:
                    raise RuntimeError(mako_exceptions.text_error_template().render())
            if type(self.output) == unicode: ##HTTP doesn't like unicode
                self.output = self.output.encode('utf-8')
            if not type(self.output) == str:
                raise TypeError('Function returned as a %s' % cgi.escape(str(type(self.output))))
            if not len(self.output):##Triggered None Length Error
                raise TypeError('Function ' + route_function['function'].__name__ + ' returned length of 0')
        except RerouteError, ex:
            route = self.internal_routes[ex[0]['name']]
            if ex[0]['message']:
                self.environ['MARIE_URL_ARGS']=[ex[0]['message']]##Replace URL args with our message
            else:
                self.environ['MARIE_URL_ARGS']=[]
            self.run_function(route)
        except:
            tb= traceback.format_exc()
            self.status='500 Server Error'
            if not route_function['debug']:
                self.error_500()
            else:
                self.output='<h3>Error</h3><pre>%s</pre>'% tb.replace('\n','<br>')
                self.output+='<h3>Environ</h3>' + str(self.environ)

    def get_args(self,func):
        if not func or not func['args']:
            return []
        args = []
        for i in xrange(func['args']-1):
            if i < len(self.environ['MARIE_URL_ARGS']):
                args.append(self.environ['MARIE_URL_ARGS'][i])
        args.insert(0,self.environ) ##First is always the environ
        return args
        
    def set_cookies(self):
        if not 'HTTP_COOKIE' in self.environ or not self.environ['HTTP_COOKIE']:
            return Cookie.SimpleCookie()
        else:
            return Cookie.SimpleCookie(self.environ['HTTP_COOKIE'])

    def check_auth(self):
        auth=Auth()
        session=auth.check_session(self.environ)
        self.environ['MARIE_SESSION']=session
        return session
    
    def get_path(self):
        path = self.environ['PATH_INFO'].rstrip('/')
        if not path:
            path='/'
        return path
    
    def get_route(self,auth,method,path):
        if auth:
            current_route=self.auth_routes
        else:
            current_route=self.unauth_routes           
        if not method in current_route:
            if auth and not method in self.unauth_routes:
                return self.error_404
        while len(path)>0:
            if method in current_route:
                if path in current_route[method]:
                    self.environ['MARIE_URL_ARGS']=self.set_url_args(path)
                    return current_route[method][path]
            if auth:
                if method in self.unauth_routes:
                    if path in self.unauth_routes[method]:
                        self.environ['MARIE_URL_ARGS']=self.set_url_args(path)
                        return self.unauth_routes[method][path]
            if len(path)<2:
                break
            path=path.rpartition('/')[0] ##Prepare for the next iteration
            if len(path)==0:
                path='/'
        return self.error_404()
    
    def set_url_args(self,short_path):
        current_path=self.environ['PATH_INFO']
        current_path=current_path[len(short_path):]
        url_args=current_path.split('/')
        for url in url_args:
            if not url or url ==' ':
                url_args.remove(url)
        if url_args and url_args[0]=='':
            url_args.remove('')
        for i in range(len(url_args)):
            url_args[i]=cgi.escape(url_args[i])
        return url_args
        
    def error_404(self):
        self.environ['MARIE_STATUS']='404 Not Found'
        log('File was not found')
        log(self.environ)
        if 404 in self.internal_routes:
            return self.internal_routes[404]
        return {'function':page_not_found, 'args':0, 'debug':False,'template':None}

    def error_500(self):
        if  self.environ['MARIE_STATUS']=='500 Internal Server Error':
                self.output=error_script()
                log('Problem with error page.')
        else:
            self.environ['MARIE_STATUS']='500 Internal Server Error'
            log('An error has occured at ' + self.environ['PATH_INFO'])
            log(str(self.environ))
            if 500 in self.internal_routes:
                self.run_function(self.internal_routes[500])
            else:
                self.output=error_script()        

    def __iter__(self):
        self.environ['MARIE_HEADERS']._add_cookies(self.environ['MARIE_COOKIES'])
        response_headers = self.response or self.environ['MARIE_HEADERS'].output()
        status = self.status or self.environ['MARIE_STATUS']
        self.start(status, response_headers)
        yield self.output


class BaseInput:
    "Base object for data input (Query String or Post Body)"
    def __init__(self,environ):
        self.environ=environ
        self.data=None

    def get(self,key=None, escape=True):
        self.escape=escape
        if not self.data:
            self.parse()
        if not key:
            return self.data
        if not key in self.data:
            return None
        return self.data[key]


class Qrs(BaseInput):
    "Query string object"
    def parse(self):
        get = urlparse.parse_qsl(self.environ['QUERY_STRING'])
        self.data={}
        for pair in get:
            if self.escape:
                self.data[pair[0]]=cgi.escape(pair[1])
            else:
                self.data[pair[0]]=pair[1]


class Body(BaseInput):
    "Post body object"
    def parse(self):
        env=self.environ.copy()
        env['QUERY_STRING'] = ''
        post = cgi.FieldStorage(fp=env['wsgi.input'],environ=env,
                                keep_blank_values=True)
        self.data={}    
        for key in post.keys():
            if type(post[key])==list: ##Lists (select objects)
                d_list=[]
                for i in range(len(post[key])):
                    entry = post[key][i].value
                    if self.escape:
                        entry = cgi.escape(entry)
                    d_list.append(entry)
                self.data[key]=d_list
            elif post[key].type=='text/plain' or not post[key].type: ##Text (multiform or url-encoded)
                entry = post[key].value
                if self.escape:
                    self.data[key] = cgi.escape(entry)
                else:
                    self.data[key] = entry
            elif post[key].type: ##Images and file uploads
                self.data[key]={'value':post[key].value, 'type':post[key].type}
        

def expose(path, function,method='GET', auth=False, template=None, debug=False):
    """Exposes functions to URLs. Creates dictionary with information and
    modifies the application class by storing new dict in either authorized
    or unauthorized routes."""
    method = method.upper()
    path.rstrip('/')
    if len(path)==0:
        path='/'
    if auth:
        active_route=application.auth_routes
    else:
        active_route=application.unauth_routes
    if not method in active_route:
        active_route[method]={}
    spec = len(inspect.getargspec(function).args)
    active_route[method][path]={'function':function, 'debug':debug,
                                'args':spec, 'template':template}

def internal(name, function, template=None, debug=False):
    "Stores internal functions are not exposed but are full featured."
    spec = len(inspect.getargspec(function).args)
    application.internal_routes[name]={'function':function, 'debug':debug,
                                       'args':spec, 'template':template}

def reroute(name,message=None):
    raise RerouteError({'name':name, 'message':message})

def add_cookie(environ,key,value,max_age=None,secure=False):
    '''Adds cookie to environ to be added to header at time of response.
    Example:
        marie.add_cookie(environ,'name','Marie',300,True)'''
    environ['MARIE_COOKIES'][key]=value
    environ['MARIE_COOKIES'][key]['path']='/'
    if max_age:
        environ['MARIE_COOKIES'][key]['max-age']=max_age
    if secure:
        environ['MARIE_COOKIES'][key]['secure']=True
        
def read_cookies(environ):
    "Returns dict of cookies from environ."
    cookie_object=environ['MARIE_COOKIES']
    output={}
    for cookie in cookie_object:
        output[cookie]=cookie_object[cookie].value
    return output

class HTTP_Headers:
    def __init__(self,Content_type='%s; charset=%s' % (content_type,encoding.upper())):
        self.headers={'Content-type':Content_type}
        self.cookies=[]
        
    def output(self):
        output=[]
        for header in self.headers:
            output.append((header,str(self.headers[header])))
        for cookie in self.cookies:
            output.append(('Set-Cookie',cookie))
        return output
    
    def add_header(self,key,value):
        'Adds or replaces header'
        self.headers[key]=value
        
    def rem_header(self,key):
        'Removes header by key'
        if key in self.headers:
            self.headers.pop(key)
    
    def _add_cookies(self,Cookie_object):
        'takes a cookie object and adds it to list'
        cookies = Cookie_object.output(None,'','\n')
        cookies = cookies.split('\n')
        for cookie in cookies:
            self.cookies.append(cookie.strip())

##Database abstractions
class DB:
    def get(self, key):
        value = self.conn.get(key)
        if not value:
            return
        return json.loads(value)
        
    def set(self, key, value, replace=True):
        if replace:
            return self.conn.set(key,json.dumps(value))
        else:
            return self.conn.setnx(key,json.dumps(value))
        
    def keys(self,string='*'):
        return self.conn.keys(string)
        
    def expire(self,key,time):
        return self.conn.expire(key,time)
        
    def delete(self,key):
        return self.conn.delete(key)


class User(DB):
    def __init__(self):
        self.conn=Redis(db=user_db)


class Registration(DB):
    def __init__(self):
        self.conn=Redis(db=registration_db)


class Session(DB):
    def __init__(self):
        self.conn=Redis(db=session_db)
        
    def get(self, key):
        return self.conn.get(key)
        
    def set(self, key, value, replace=True):
        if replace:
            return self.conn.set(key,value)
        else:
            return self.conn.setnx(key,value)

def redis_info():
    if not Redis:
        return '<b>Redis library not installed</b>'
    conn=Redis()
    output = ['<h2>Redis Info</h2>']
    if not json:
        output.append('<h2>Error: JSON library not installed.</h2>')
    try:
        info = conn.info()
    except:
        return '<b>Unable to connect to Redis.</b>'
    for item in info:
        output.append('<b>%s</b>: %s<br>' %(item, info[item]))
    return ''.join(output)
    
    
class Auth:
    def register_user(self,user):
        if not user:
            return False
        uDB = User()
        if not uDB.keys(user.lower()):
            self._create_user(uDB,user)
        rDB = Registration()
        reg_id=hashlib.sha256(user+str(time.time())+salt).hexdigest()
        rDB.set(reg_id, user.lower())
        rDB.expire(reg_id,60*60*24) ##Expire in a day
        return reg_id
            
    def _create_user(self,db,user):
        user_json={'username':user,
                   'password':''
                    }
        db.set(user.lower(),user_json,False)
        
    def change_password(self,reg_id,username,password):
        rDB = Registration()
        db_user=rDB.get(reg_id)
        if not db_user or not db_user==username.lower():
            raise  ValueError('User does not match registration')
        rDB.delete(reg_id)
        uDB = User()
        user_json = uDB.get(db_user)
        pass_hash=hashlib.sha256(password+salt).hexdigest()
        user_json['password']=pass_hash
        if not uDB.set(db_user,user_json):
            raise IOError('Password not saved')
        rDB.delete(reg_id)
        return True

    def new_session(self,environ,user):
        "Assumes user is authorized"
        session_id=hashlib.sha256(user+str(time.time())+salt)
        session_id=session_id.hexdigest()
        sDB = Session()
        sDB.set(session_id,user)
        sDB.expire(session_id,session_lease)
        add_cookie(environ,'session_id',session_id,secure_cookie)
        add_cookie(environ,'user',user)

    def check_session(self,environ):
        'Returns False or username'
        c=read_cookies(environ)
        if not 'user' in c:
            return False
        if not 'session_id' in c:
            return False
        sDB = Session()
        session_data=sDB.get(c['session_id'])
        if not session_data:
            return False
        if not c['user']==session_data:
            return False
        return str(session_data)
    
    def authorize_user(self,user,password):
        if not user or not password:
            return False
        uDB=User()
        user_json = uDB.get(user.lower())
        if not user_json:
            return False
        pass_hash = hashlib.sha256(password+salt).hexdigest()
        if user_json['password']==pass_hash:
            return True
        return False
    
    def close_session(self,environ):
        c=read_cookies(environ)
        if not 'session_id' in c:
            return
        sDB = Session()
        sDB.delete(c['session_id'])

def redirect(environ,url,status='303 See Other'):
    'Sets environ to redirect and returns html redirect page'
    environ['MARIE_STATUS']=status
    environ['MARIE_HEADERS'].add_header('Location',url)
    return '<h3>Redirecting to <a href=%s> another page</a>.</h3>' % url

def run(port=80):
    httpd = make_server('', port, application)
    print "Python WSGI webserver is now running on port %d" % port
    httpd.serve_forever()
