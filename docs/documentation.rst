Marie Code Documentation
************************

Globals
==============

.. py:data:: content_type

    STR. Sets default content type for all responses. Default is "text/html"

.. py:data:: encoding

    STR. Sets default document encoding. Default is "utf-8"

.. py:data:: error_file

    STR. Sets the location and name of the error log file. Default is ``None``.

.. py:data:: salt

    STR. Sets the salt for password encryption.

.. py:data:: secure_cookie
    
    BOOL. Sets whether Marie will require authorization cookies to be set secure
    only. Requires SSL. Default is ``False``

.. py:data:: session_lease

    INT. Sets time to live for sessions. Default is 60*60*24 or 1 day.

.. py:data:: user_db
    
    INT. Sets the Redis database for user information. Default is 0.

.. py:data:: registration_db

    INT. Sets the Redis database for registrations. Default is 1.

.. py:data:: session_db
    
    INT. Sets the Redis database for storing sessions. Default is 2.

.. py:data:: template_dirs

    LIST. List of directories which contain templates. Default is ['.']

.. py:data:: template_bytecode_dir

    STR. Location of temporary bytecode directory. Default is ``None``.

.. py:data:: template_updates
    
    BOOL. Checks to see if newer version of templates exist. Default is ``True``.

Default Scripts
===============

.. py:function:: error_script()

    The default message for errors.
    
.. py:function:: page_not_found()

    The default message for 404s.
    
Errors and Logging
==================

.. py:function:: log(error)

    Saves message to error log.
    
.. py:exception:: RerouteError

    Used for catching reroutes to internal routes
    
Marie Application Class
=======================

.. py:class:: application

    The WSGI Application yields output according to PEP 333
    
    .. py:method:: choose_function()
    
        Chooses appropriate function
        
    .. py:method:: run_function(route_function)
    
        Runs the chosen function. Catches errors as found.
        
    .. py:method:: get_args(func)
    
        Creates a list for the arguments of the route function.
        
    .. py:method:: set_cookies()
    
        Returns a Cookie object of the cookies contained in the environ
        
    .. py:method:: check_auth()
    
        Returns if user is authorized
        
    .. py:method:: get_path()
    
        Returns the URL path
        
    .. py:method::get_route(auth,method,path)
    
        Returns the appropriate route function.
        
    .. py:method:: set_url_args(short_path)
    
        Returns list of URL arguments
        
    .. py:method:: error_404()
    
        Returns route for 404 page.
        
    .. py:method:: error_500()
    
        Returns route for 500 page.
        
    .. py:method:: __iter__()
    
        Yeilds WSGI output
        
Data Input QRS and Body
=======================
        
.. py:class:: BaseInput

    Base object for data input (Query string or Post body)
    
    .. py:method:: get(key=None,escape=True)
        
        Returns data
        
.. py:class:: Qrs
    
    Query string object

    .. py:method:: parse()
    
        Parses query string and saves in object
        
.. py:class:: Body
    
    Post body object
    
    .. py:method:: parse()
    
        Parses query string and saves in object
        
    
Route Expose Functions
======================

.. py:function:: expose(path, function [, method='GET', auth=False, \
                        template=None, debug=False])
    
    Exposes functions to URLs. Creates dictionary with information and modifies
    the application class by storing new dict in either authorized or
    unauthorized routes.
    
.. py:function:: internal(name, function [,template=None, debug=False])
    
    Stores internal functions that are not exposed, but are full featured.
    
Utility Functions
=================

.. py:function:: reroute(name [,message=None])
    
    Stops function execution and restarts with internal function.
    
.. py:function:: add_cookie(environ, key, value [, max_age=None, secure=False])

    Adds cookie to environ to be added to header at time of response.
    
.. py:function:: read_cookies(environ)
    
    Returns a dict of cookies from environ.
    
.. py:function:: redirect(environ,url [,status='303 See Other'])

    A returnable function for redirects.

.. py:function:: run([port=80])

    Starts webserver
    
HTTP Headers
============
    
.. py:class:: HTTP_Headers
    
    Class for manipulating Headers
    
    .. py:method:: output()
        
        Returns headers.
        
    .. py:method:: add_header(key,value)
    
        Adds or replaces headers
        
    .. py:method:: rem_header(key)
    
        Removes header by key
        
    .. py:method:: _add_cookies(Cookie_object)
    
        Takes a Cookie object and adds it to headers.
        
Authorization and Database
==========================

.. py:class:: DB
    
    Base class for database abstraction
    
    .. py:method:: get(key)
    
        Returns value of key
        
    .. py:method:: set(key, value [, replace=True])
    
        Sets value to key
        
    .. py:method:: keys([string='*'])
    
        Returns list of keys
        
    .. py:method:: expire(key,time)
    
        Sets expiration of database item.
        
    .. py:method:: delete(key)
    
        Deletes database object  
    
.. py:class:: User

    Class for user database
    
.. py:class:: Registration

    Class for registration database
    
.. py:class:: Session

    Class for session database
    
    .. py:method:: get(key)
    
        Returns value of key
        
    .. py:method:: set(key, value [, replace=True])
    
        Sets value to key

.. py:function:: redis_info()

    Returns redis info
    
.. py:class:: Auth

    .. py:method:: register_user(user)
    
        Creates a newly registered user.
        
    .. py:method:: _create_user(db,user)
    
        Creates user object and stores it in DB
        
    .. py:method:: change_password(reg_id, username, password)
    
        Changes user password and saves to DB. Returns ``True`` if successful.
        
    .. py:method:: new_session(environ, user)
    
        Creates new session for user and stores in db and cookies.
        Assumes user is authorized. Should run ``authorize_user`` first.
        
    .. py:method:: check_session(environ)
        
        Check session to see if user has session.  Returns Bool.
        
    .. py:method:: authorize_user(user, password)
    
        Checks to see if user is authorized.
        
    .. py:method:: close_session(environ)
    
        Removes session from database.