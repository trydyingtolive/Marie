Marie Manual
************


Introduction
============

Why Was Marie Created?
----------------------
Marie was written out of a desire to have a safe and quick method of creating simple Python web applications. I had tried and was ultimately unsatisfied with the core decisions of the few micro-frameworks there were at the time. Therefore, I set out to make a framework that suited the kind of things I was doing.

That framework, which I called Marie, evolved over the course of several projects. Eventually, the code reached a place where each application didn't require a major change or a new feature added. The result is a deliciously simple, incredibly fast WSGI micro web framework.

What to expect from Marie
-------------------------

**Take the rough edges off.**
    Things as simple as getting a URL to respond to the write script can be an annoying task.  Headers, redirects, cookies, sessions, POSTs, Unicode compatibility, configuring, and URL arguments are not any more fun. Marie aims to help you get the info you need and send back your reply as simply as possible.
**Quick**
	Marie was designed to be light on her feet, and not just in a 'Hello World' benchmark. Request bodies, URL arguments, and query strings have a tendency to slow down frameworks even if the application doesn't use them. Marie stays fast by either pre-parsing information or by only parsing the information you ask for, up to twice as fast in some situations.
**Simple**
	Simplicity isn't just for speed and ease of use, it's also for hackability. Don't like the way Marie does something? Change it! Marie has a dozen different configuration variables that are easy and straight forward to set.  If that isn't enough for you, Marie is a single file about 500 lines; dive right into the code and hack away. We've even set up a section in the documentation if you want to change something.
**Environ Overloading**
	Marie uses and abuses the environ dictionary. Marie shoves a ton of information into the environ. This is the main way information about the request is passed to the function.  This information isn't only the raw stuff from the server.  Nope, Marie adds in objects that are easy and fast to read and edit. As an added bonus certain changes made to the environ are passed back to the server.
**Redis**
	Marie was designed to be quick and simple, and Redis keeps our sessions conformed to our goals. Redis is a disk backed in memory key value store.  Using Redis or the built in sessions is optional, and using your own session scheme is possible.
**Mako**
	Mako is a powerful yet fast templating engine. Marie makes using Mako just as simple as not using templates. Using Mako is optional.

Routing
=======

Introduction
------------
Let's jump right in with a quick hello world app. Create a new file we'll call it MyApp.py. Make sure that Marie is in the same directory with your new file. Add this code to MyApp.py: ::
    import marie

    def index():
        return "Hello World" 
    marie.expose('/', index)
    
    marie.run()

Deliciously simple, eh? Of course it is! It only produces "Hello World" after all. Run your application and then steer your browser to  127.0.0.1 and see your creation. You are a hero. 

Let's dig in and see what all this is. Line 1 simply imports Marie. This is why you needed marie.py to be located in the same directory as your application. Python had to be able to find it. The easiest way is to simply save them in the same place.

Line 3 and 4 are our simple function. Line 5 is where the magic happens, we are telling Marie about our function and that whenever someone visits the root directory ('/') they should be given the output of index(). Finally marie.run() starts the webserver for us. 

Tip: If you are running Marie's web server on Linux or OSX you may need to run your server using the sudo command, though be careful as this would give your website the powers of root.

Tip: If at any point you would like to stop Marie's web server from running simply use Python's built-in keyboard interrupt: Ctrl + C.

Routing Basics
--------------
Routing is the primary purpose of Marie. This gives us an easy and quick way to have our URL's point to different functions. Let's do another more advanced illustration. ::

    import marie
    
    def index():
        return "Hello World"
    marie.expose('/', index)
    
    def route():
        return "This routing is pretty cool"
    marie.expose("/routing", route)
    
    marie.run()

Now take your browser to "127.0.0.1/routing". When we went to /routing Marie used the route() function. If you travel to the root directory '/' you will see the output index() again. You have just discovered one of the most important features of Marie's routing. Marie will first try to match the longest URLs before trying a shorter and shorter version of the URL (within the same HTTP method). What does this mean? If you go to "/routing/doesnotexist", instead of giving you a 404 error, Marie will first try the shorter URL of "/routing". More importantly it will progressively try shorter and shorter URL's meaning you can stack as many arguments in the URL as you want. Later on we will show you how to access those arguments.

Note: Exposed URL's should begin with a '/'. 'routing' would be incorrect, '/routing/' would be ill advised, but '/routing' will bring success.

Debugging
---------
You may have noticed already that, if you make a mistake and make a runtime error, Marie will catch it and present a non-descript error page.  This isn't very handy for figuring out what is wrong. In order to find out the error simply enable debugging when you expose a function. ::
    def index():
        return IAmAnError
    marie.expose('/', index, debug=True)
If you run your code it will produce a full traceback and a dump of the environ. Be sure to remove the debug attribute before publishing your application as the traceback can cause security issues.

Route Stacking
--------------

This would be a good time for some example of route stacking. In this example we will expose 3 functions to URLs. ::

    def index():
        return "Hello World"
    marie.expose('/', index, debug=True)
    
    def blog():
        return "Blog Index"  ##Add pages when I learn about URL arguments
    marie.expose('/blog', blog, debug=True)
    
    def blog_admin():
        return "Admin Page"
    marie.expose('/blog/admin', blog_admin, debug=True)
    
In this example we have a home page at '/' for index(); a blog at '/blog'  for blog(); and a admin page for the blog at '/blog/admin' 

*   The user requests "/blog/page/1"
    
    *   Marie tries at the url "/blog/page/1" and finds nothing
    *   Marie tries at the url "/blog/page" and finds nothing
    *   Marie tries at the url  "/blog"  and runs the function blog()

*   The user requests "/blog/admin"

    *   Marie tries the url "/blog/admin" and runs the function blog_admin()

*   The user request "/blaaged/admin" 

    *   Marie tries the url "/blaaged/admin" and finds nothing
    *   Marie tries the url "/blaaged" and finds nothing
    *   Marie tries the url "/" and runs the function index()

I hope that the goals of this routing method are clear to you. It means that your application is more likely to resist 404's and it allows for your URLs to be as flexible as you want them to be.

Methods
-------
The final topic in the basic overview of routing is methods. So far all of our examples used the HTTP GET method. This alone will simply not cut it. These are the days of REST we need more methods! Good news, changing the method is ultra easy. ::

    def index(environ):
        return "Hello World"
    marie.expose('/', index, debug=True)
    marie.expose('/', index, 'POST', debug=True)

Ok, I threw two things at you. First of all you notice there are two marie.expose(). That is because you can route a function to different URL's the first is to the root directory for a GET and the second is for the root directory for a POST. You can expose to any HTTP method your server can handle. It is important to note that in this example a GET request to '/' and a POST request to '/' will be fulfilled, but no other method. You have to expose to each method individually.

Environ
=======

Introduction
------------

WSGI generates quite a bit of information about each and every request. This is a good thing, it means we get plenty of information to work with, and information is fun to play with. This request information is passed on to us via a Python dictionary called the "environ". Marie uses a design I like to call "environ overloading". In short nearly everything is done through the environ. Form input, cookies, headers are all passed to the functions via the environ, and any changes made to the environ, such as headers, are passed back to the server.  If you've ever had to spend time sifting through documents about how to read and set cookies or worse process a POST, you will appreciate that Marie will take care of the tedious stuff.

To start let's take a peek at your environ. ::

    import marie
    
    def index(environ):
        return str(environ)
    marie.expose('/',index, debug=True)
    
    marie.run()

First of all notice that we have added one argument to our function. This argument is optional, but note that the first argument of any exposed function will be passed the environ.

Go to "127.0.0.1" and you'll get to see all sorts of information. It's in a sort of mixed unsorted jumble. That's ok; if you are familiar with WSGI all of the standard information is there. What I do want to draw you attention to all of the keys that start with the word "MARIE" these are the special bits added by the framework to make your life easier.

URL Arguments
-------------
Remember all that hubbub we went through in the routing section? How you can have a URL of any length and Marie will try and find the longest matching route. In the above example you could have a URL "/blog/page/1" and Marie would match it to "/blog". Now we want to know which page that blog was on if any. 

Function Arguments
^^^^^^^^^^^^^^^^^^

The most straight forward way of getting these arguments is to simply add them as arguments in your exposed function. ::

    def blog(environ, location='home', page='0'):
        return 'The location is "%s", and the page is "%s" ' % (location,page)
    marie.expose('/blog',blog, debug=True)
    
If you aren't very familiar with Python or programming this may be a little confusing, but it is a serious shortcut. If you check out "/blog/page/1" you will see the following message 'The location is "page", and the page is "1"'. You can change or remove the URL arguments to see how the message changes.

There are a few things that are going on. First of all Marie will only pass arguments you ask for. This means ``*args`` won't work. Secondly, Marie will only pass arguments if they exist, so every argument needs a default value. Third if there are more URL arguments than there are arguments in your exposed function Marie won't try and pass those (Marie only passes arguments you request). 

It is important to note again that the first argument will always be the environ.

MARIE_URL_ARGS
^^^^^^^^^^^^^^

Sometimes you want to make sure that you get all of your URL arguments. This is where MARIE_URL_ARGS comes in. MARIE_URL_ARGS is a list of all the parts of the url that aren't part of the route used. In the example of our blog (/blog/page/1) MARIE_URL_ARGS would return ['page', '1']. Let's modify our above code to take a look at this

def blog(environ):
    output="The URL  args are: <br>"
    for arg in environ['MARIE_URL_ARGS']:
        output+="<br>"
        output+=arg
    return output
marie.expose('/blog',blog, debug=True)

This function simply iterates through environ['MARIE_URL_ARGS'] and adds it to a list. Now visit '/blog/item1/item2/a third item' and see what you get. Change the number of arguments and experiment. You can see how this would be a handy way of passing information to the server, but it isn't the only way. Marie automatically escapes all HTML from the URL arguments.

Form Data
---------

The MARIE_QRS and MARIE_BODY objects are a simple way of receiving the input of forms and other HTTP Requests. MARIE_QRS retrieves the information stored in the query string used by GETs. Input provided by a POST is located in MARIE_BODY. Retrieving the information within is as simple as calling the get([key]) method. Omitting a key will return a Python dictionary of all the data.

MARIE_QRS.get([key]) and MARIE_BODY.get([key]) will return the values in three possible ways: as a string, a list, or a dictionary. Strings are returned for single value type elements such at text boxes and hidden fields. Lists are used when a key can have more than one value such as for a multi-select or checkboxes. A dictionary is used for file uploads. The dictionary contains two pairs: 'type' for the mime-type of the file and 'value' for the binary of the file. ::
    def index(environ):
        name = environ['MARIE_QRS'].get('name') or 'World'
        return '''Hello %s
    <form action=/ method='POST'>
    <input name=name>
    <input type=submit>
    </form>''' % name
    marie.expose('/', index, debug=True)
    
    def p_index(environ):
        name = environ['MARIE_BODY'].get('name') or "Yellow"
        return 'Jello %s' %name
    marie.expose('/',p_index, 'POST', debug=True)
    
Marie automatically escapes all of the HTML that may be in the form data. This helps protect your web application is protected against some XSS attacks. This might or might not be what want depending on what you are doing. Use the argument "escape=False" to access the unescaped input. ::

    raw_input = environ['MARIE_BODY'].get('name',escape=False) 
    raw_qrs = environ['MARIE_QRS'].get(escape=False)

MARIE_STATUS
------------

MARIE_STATUS is the simple way to read and write the status code for the response. Marie sets the code as the default of "200 OK" for you, but you are free to change the code as your project dictates.


Advanced Environ
================

Cookies
-------

Marie passes a standard Python cookie object through the environ. It is the value of the environ key MARIE_COOKIES. You can use the object to both read and set cookies.  An example function that uses the MARIE_COOKIES would be this: ::

    def cookie(environ):
        c = environ['MARIE_COOKIES']
        if not 'count' in c:
            c['count']=1
            return 'This was your first visit'
        c['count'] = int(c['count'].value)+1
        return "You have visited this many times: %s" % c['count'].value
    marie.expose("/cookie", cookie, debug=True)

Using the Python cookie object gives us plenty of access to read, modify, and add cookies. This way you have plenty of power over your cookies. For more information read the documentation in the Python standard library docs.

Marie even has an easier pair of tools to help you read and write cookies a tiny bit easier. ::

    marie.read_cookies(environ)  ## Returns dict of cookies
    marie.add_cookie(environ, key, value, max_age=None, secure=False)

The above example using these tools would look like: ::

    def cookie(environ):
        c = marie.read_cookies(environ)
        if not 'count' in c:
            marie.add_cookie(environ, 'count', 1)
            return 'This was your first visit'
        count = int(c['count']) + 1
        marie.add_cookie(environ, 'count', count)
        return "You have visited this many times: %s" % count
    marie.expose("/cookie", cookie, debug=True) 

Which way you read and set cookies is up to you. Using the shorter functions may be easier, but the longer way will give you more control.

Headers
-------

The ability to set headers can be very important to you.  Redirects and other advanced options require you to be able to manage your HTTP headers. Guess what! Marie passes all that information through the environ dict.  ::

    def example(environ):
        headers = environ['MARIE_HEADERS'] ##Headers object
        headers.add_header("Location", "http://google.com")
        headers.output() ##returns list of headers
        headers.rem_header("Location") ## Remove header

Here is a quick shortcut for redirects. Rather than changing the header, and status yourself Marie will do all the hard work for you. Just return the redirect function. Setting the status is optional and defaults to 303 See Other. ::

    def redirect(environ):
        return marie.redirect(environ, "http://google.com",  status="303 See Other")
    marie.expose('/redirect',redirect, debug=True)

Templates with Mako
===================

Marie has support for Mako templates out of the box. You will of course need to have Mako installed on your system, but after that Marie makes it easy. We'll take care of all of the Unicode, directories, and error handling. Notice that we return a dictionary rather than a string. ::

    import  marie
    
    marie.template_dirs.append("/location/of/templates")
    
    def index(environ, name="No One"):
        return {"name":name}
    marie.expose("/",index, template="example.html")

If you have an error simply add debug=True to marie.expose(). Any errors related to the template will display Mako's built in debugging tools.

For more information on how to use Mako visit http://www.makotemplates.org/

Note: There are other options for Mako. See Properties (and Defaults) in the Modifying Marie section.

Internal Routing
================

How to Use
----------

Suppose you want to redirect to another function without using an HTTP redirect? Well Marie has a feature for you. It's called internal routing and it can be a very helpful tool. Rather than exposing a function to a URL like you would normally, you name your function so Marie can find it later. For example let's say you have users fill out a form. If a required part is blank you can reroute them back to the form with the missing fields highlighted. Internal routes have all the features of a normally routed function. ::

    def fail_login():
        return 'We are sorry, but the login failed'
    marie.internal('fail',fail_login)
    
    def incomplete_form(environ, message='Unknown part'):
        return 'You need to fill out this part of the form: %s' % message
    marie.internal('fail',incomplete_form)

You may have noticed that this looks like a normally exposed function, and mostly it is. The only major difference is you use marie.internal() rather than marie.expose(). Also note that since this is an internally referenced function there are a couple of other differences. First rather than exposing the function to a URL, we give it a name so we can ask Marie for it later. Second since our function isn't exposed to the outside world there is no method argument nor is there an authorization argument. Third Marie will rewrite environ['MARIE_URL_ARGS'] with your message information. You can still set debug=True if you want and internal routes also support templates.

Switching to an internal route is as simple as creating one. Simply use ``marie.reroute(name, message)`` ::

    def we_know():
        return 'We know who you are Marie'
    marie.internal('we_know',we_know)
    
    
    def index(environ, name=None):
        if name=="Maire ":
            marie.reroute('we_know')
        else:
            return "Welcome! "
    marie.expose('/', index)

In this example if you visit /Marie you will be rerouted to the internal route of we_know(). We can also send a message. ::

    def we_know(environ, message='Mystery'):
        return 'We know who you are %s' % message
    marie.internal('we_know',we_know)
    
    def index(environ, name=None):
        if name:
            marie.reroute('we_know', name)
        else:
            return 'Who are you?'
    marie.expose('/', index)

In this case a message is sent to the rerouted function. This way you can send information from the first route to the next. This example showed sending a message as a string, but you can send other things like dictionaries and objects as messages. And yes, you can chain multiple reroutes.

Special Internal Routes
-----------------------

There are two special internal routes which are related to error messages. Marie will only ever throw a 500 Internal Server Message or a 404 Not Found error on her own. You can change the way these two error pages look by creating internal routes for them. ::

    def error_404():
        return 'Sorry, We lost your page!'
    marie.internal(404,error_404)
    
    def error_500():
        return 'Whoa! What did you do?'
    marie.internal(500,error_500)

These two special errors work almost identically to regular internal routes except for a few things. First you cannot pass messages, so don't even try. Secondly they have specific names to be routed to. The 'Not Found' error needs to be named the int 404 and the 'Internal Sever Error' must be named the int 500. Other than that they can use templates and debug like every other route type.

It should be noted that if your 500 function throws an error, Marie will still catch it and display her default error page.

Authorization
=============

Introduction
------------

Marie comes with a simple authorization scheme. With sessions you can easily separate the parts of your site that require authorization from the parts for the general public.

The authorization scheme requires three things to make it work. First of all you will need the Redis database. Redis is a key value storage system that resides in memory. Unlike a cache such as memcached, Redis regularly saves the data disk making it both persistent and fast.

You will also need the Python library for Redis and in a location that is accessible to Marie. Note that simply placing the library in the same location as Marie or your application may not be enough to let Marie import the library. You may need append the system path or move the library to the proper directory.

Thirdly you will need a json library. If you are using Python 2.6 or later it's included and you are good to go. Marie will also work out of the box with simplejson. 

Note: Just because a user is authorized it doesn't mean that Marie will keep them from seeing other user's data. You have to do that yourself.

Why Redis?
----------

Redis was chosen because it's fast –blistering fast. Since Redis stores all of its data in memory, it is able to respond to requests very quickly. It is likely that you will make the most requests to your database for sessions. Every time someone tries to access a secure part of your application their session will have to be authenticated. There is no reason to keep hitting the disk. Keep it in memory and keep it fast.

Another important feature of Redis is its simplicity. Redis is a key value storage. This means that it is very easy to use and even easy to modify and hack the way Marie interacts with it. Rather than using a schema Marie stores user information in JSON strings.

For more information on Redis visit http://www.redis.io 

Three Step Process
------------------

Marie uses a three step system to create users.  First you create a new user. This new user exists, but has no authorization authority.  Second, when you create a new user Marie will give you a registration code. This registration code is then needed to set a password.  Finally, the user can have his password set and is now an authorized user.

The use of a registration code seems like an extra step at first. Why not just let a user be created and given a password without the need of that extra step? The simple reason is that it's easier to bypass the extra step than to create that step if needed. Let's take an example.

Your website allows users to register in order to leave comments. However, you want to make sure that they have legitimate e-mail addresses.  So you create a form that has two inputs "username" and "email".  When a new user signs up you want to email them a link to let them finish the registration process.

Your site then creates a new user using the provided username. Marie returns a registration code. You can then send that registration code via email. Your users can copy that code and paste it in a form along with their new password. When they are done they can log in.

That's a nice feature to have built in. If you don't want confirm email addresses you can have your application automatically complete that step.

Checking Redis
--------------

There is a simple tool included with Marie to make sure that Redis is set up and ready: marie.redis_info() ::

    def redis():
        return marie.redis_info()
    marie.expose('/redis', redis, debug=True)

Simply visiting /redis will either tell you what isn't working or give you an info page on your Redis server.


Creating Authorized Users
-------------------------

Let's make a quick application. Nothing fancy, just a way to show how to create users and start sessions. ::

    import marie

Our app starts by importing the Marie Framework. Next we will make our index page for non authorized users. Folks who haven't logged in will see this function. It simply contains a form to log in and a link to make new users. ::

    def non_auth():
        output = """
    You are not logged in!
    <form method=post action=/login>
    Log-in:<br>
    User:<input name=username><br>
    Pass:<input name=password type=password><br>
    <input type=submit value='Log in'>
    </form>
    <a href=/new>Or create a new account</a>
        """
        return output
    marie.expose('/',non_auth)
    
Next we will make an index page for folks who are logged in. It displays the username found in one of the session cookies. Notice that this function is also exposed to the root directory, except that this time it has the authorization variable set to True. This means that there are two functions for the same URL: one for people logged in and on for those who aren't. ::

    def authorized(environ):
        output = '''Hi %s! You are now authorized.
    <br> <a href=/logout>Logout</a>
    ''' % environ['MARIE_SESSION']
        return output
    marie.expose('/', authorized, 'GET', True)
    
This next function is a simple form to create a new user. It is important to note than this function is exposed as the default 'GET' method. The form points to the same URL (/new) but with a POST method. The username is located in environ['MARIE_SESSION']. ::

    def new_user():
        output= """
    Create a new user.
    <form method=post action=/new>
    User:<input name=username><br>
    Pass:<input name=password><br>
    <input type=submit value="Create New User"
    </form>"""
        return output
    marie.expose('/new', new_user)

When the form is submitted it is submitted to this function. Notice that it is exposed as a POST rather than a GET. This takes the form data and checks to make sure they aren't blank. If they are it will throw a specialized error message saying 'Fields may not be blank'. The next line accesses the authorization object. We then use that authorization method to create a new user. The server will return a registration id. Since we don't want to confirm an e-mail address for this example we will then use that registration id immediately to set the user's password. (If you are keeping track we completed the three steps of registering a new user in two lines.) ::

    def new_user_post(environ):
        username=environ['MARIE_BODY'].get('username')
        password=environ['MARIE_BODY'].get('password')
        if not username or not password:
            raise marie.MinorError('Username and password required')
        auth = marie.Auth()
        registration = auth.register_user(username)
        auth.change_password(registration,username,password)
        return 'User created'
    marie.expose('/new', new_user_post, 'POST')
    
Now that we have created a new user we need a way to log in. This function is where the form from the unauthorized root page points to. Notice that it is exposed as a POST. After getting the username and password that were submitted, we create a new authorization object. The "if" statement tests to see if the username and password are a matching pair. If so, we create a new session that gets passes into the cookie object in the environ. Finally it returns a redirect to the root page, this time showing  the authorized version. If the username and password aren't a match they get a little message telling them so. ::

    def login(environ):
        username=environ['MARIE_BODY'].get('username')
        password=environ['MARIE_BODY'].get('password')
        auth = marie.Auth()
        if auth.authorize_user(username,password):
            auth.new_session(environ,username)
            return marie.redirect(environ,'/')
        else:
            return 'User is not authorized!'
    marie.expose('/login', login, 'POST')
    
The final function logs us out. It simply uses the authorization object to invalidate the session. Notice that the function is exposed with the authorized argument set as true. Users have to be logged in before they can log out. One thing of note is that Marie doesn't simply actually remove the session cookies from the web browser, rather it deletes the session in the database. Once the session is closed it cannot be used again. ::

    def logout(environ):
        auth = marie.Auth()
        auth.close_session(environ)
        return marie.redirect(environ, '/')
    marie.expose('/logout', logout, 'GET', True)

And last we tell Marie to start up the server. ::

    marie.run()

Note: Marie can change password too. The process is the same. Create a new user using an existing username (note this doesn't remove the original password). Marie will return a registration number. Use that number to reset the user's password. It is important that you check to see if a username already exists before adding a new user.

Authorization and Routing
-------------------------
After you get this code up and running there are a couple of things that I would like to point out about how Marie deals with authorized and unauthorized routes. First of all Marie gives priority to authorized sessions over unauthorized sessions. That's why there were two indexes exposed to the same URL. When you were not logged in you weren't allowed to see the version with the authorization set to True, so Marie routed you to the one you could see.  When you were logged in, Marie gave priority to the authorized function.

One thing you may have noticed is that when you are logged in you can still see pages that are not set as authorized. You can actually be logged in and visit /new and add another new user. That's because if Marie doesn't find an authorized version for someone who is logged in, it will give them the unauthorized version instead. The same rule still applies Marie will always route you to the longest matching URL. The only difference is when an authorized and an unauthorized function are routed to the same URL Marie will give priority to the authorized function (so long as the user is authorized.)

Note: With all this talk of authorized and unauthorized versions it is important to remind you that Marie only checks to see if a session exists. Marie will not automatically differentiate one session from another. In other words, if you want to keep data for one user from being seen by another user, you will have to do that yourself.

Customization
=============

Introduction
------------

Part of the reason Marie is so simple is so that you can change it as you please. Marie has no lack of options to customize how it works for you.

Properties (and Defaults)
------------------------

Change these variables to set the way Marie handles certain situations. The defaults are shown.::

    marie.content_type='text/html' Sets the default content type. Change to 'application/xhtml+xml' for xhtml
    marie.encoding = 'utf-8' Change the encoding. Just keep it Unicode, think of the children.
    marie.error_file = None  This is the full path to an error log file. This is important if you want to be able to read any information about errors that Marie catches.
    marie.salt = 'mariesalt' This is just a customizable salt for passwords and sessions. Change it as you please so not everyone's salt is the same.
    marie.secure_cookie=False Send session information via Secure Cookies. Requires HTTPS.
    marie.session_lease=60*60*24 Time to live set for each session after last request
    marie.user_db=0 This is the Redis database for user information
    marie.registration_db=1 This is the Redis database for registration information
    marie.session_db=2 This is the Redis database for session information
    marie.template_dirs = ['.'] List of directories for your templates.
    marie.template_bytecode_dir = None Location of temporary directory for saving precompiled versions of your templates
    marie.template_updates = True Checks to see if newer versions of the templates exist. Set False to improve speed, keep True for development.

Making Major Changes
--------------------

Marie was designed to be as simple as possible and to be as hackable as possible. These two goals don't always go hand in hand since URL routing is sort of a sketchy task. This section is just a few notes to get you started on modifying a bit deeper.
	
marie.application.check_auth is the location of the function that is used to see if the user has an authorized session or not. If you wanted to push in your own database or authorization scheme this is where you do it. If this function returns True the user is authorized; False for unauthorized. If you change this part you can rip out all of the database and authorization sections.

A quick note on how Marie stores routes. At the top of the application class you will notice three empty dictionaries. One is for authorized routes and other for unauthorized routes. When you expose a function to a route Marie will store it in the appropriate spot. For example if I exposed the function index() to the URL '/', Marie would store it as : ::

    unauth_routes["GET"]["/"]={'function':index, 'debug':False, 'args':0, 'template':None}

"function" is the actual function to be run if '/' is requested; "debug" sets what happens in case of an error; "args" is the number of arguments the exposed function has, and "template" is the location of the the optional template.

Troubleshooting
===============

The first type of error you may encounter is when there is an error that happens when code is malformed and cannot be compiled. This is the type of error that generally only comes up whenever you are making changes to you app.  Marie doesn't handle this type of error because it isn't even given a chance to get up and running. You can tell the error is cause by malformed code because all of your URLs will show the same error message. This message is generated by the server and not by Marie. Check your server's logs for extra help.

The second type of error is much more common and can easily occur on a server that is in production --a run time error. Thankfully Marie is ready to catch this kind of error. If you add "debug=True" to your marie.expose(), Marie will even print a trackback in your browser as well as the environ. Otherwise Marie will return a prepared error message and if you have logging enabled it will save the trackback and environ.

Deployment
==========

Introduction
------------

The standard python built in WSGI server is enough for most websites. On my underpowered VM I can handle about 5 requests per second. As long as you don't expect a heavy or even moderate load this may be enough for you. However, it would be a good idea to use a more capable web server. Marie should run on any WSGI 1.0 server or any WSGI 1.0 handler. Just by adding a better server I was able to increase the number of requests per second up to 1,700. Here are a couple of examples of how to deploy Marie on the WSGI compatible server of your choice. 

Apache
------

To run Marie with Apache under mod_wsgi is fairly simple but take some configuration. The first step, of course, is installing and enabling mod_wsgi. After installation use the WSGIScriptAlias directive in your site configuration to direct requests toward the correct app file. Example: ::

    WSGIScriptAlias  /blog  /var/www/pybin/blog.py
    WSGIScriptAlias  /  /var/www/pybin/index.py

To make applications able to be accessed by mod_wsgi you need to add this line to your files: ::

    application=marie.application

If Apache is unable to find Marie you may need to add the following to the top of your application: ::

    import sys
    sys.path.insert(0,'/folder/containing/marie')

Gevent
------

gevent can be used as an asynchronous wsgi web server. This makes it great for highly concurrent application.  After installing gevent, just add these two lines to the bottom of your application and run.  ::

    from gevent import wsgi
    wsgi.WSGIServer(('',80), marie.application, spawn=None).serve_forever()
