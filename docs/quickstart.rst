.. Marie documentation master file, created by
   sphinx-quickstart on Thu Apr 28 19:47:02 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started With Marie
**************************

Marie is a snap to set up and run. This document was created to get up and running as quickly as possible.

Installing Marie
=================

Marie can be installed by via PIP, easy_install, setup.py, Windows installer or by simply placing marie.py in the same directory as your web app.

PIP::

    pip install marie

easy_install::

    easy_install marie
    
To use the setup file download the source file at the `Cheese Shop <http://pypi.python.org/pypi/Marie/>`_ and uncompress and run the setup script like this: ::

    python setup.py install

The Cheese Shop also contains a Windows executable.

First Steps
===============

A Simple first Hello world application is as follows: ::

    import marie
    
    def index():
        return "Hello World"
    marie.expose('/', index)
    
    marie.run()
    
In the first line we import the Marie framework. Next we create a function that
will return a string. It returns the words "Hello World". The next line
"exposes" the root document to our function. The last line starts our server.

If you run the program and turn your browser to http://localhost/ (or the IP of the
server) you will see the message "Hello World" Our next example will be
slightly more complex, but will give us a dynamic result. ::

    import marie
    
    def index(environ, name="World"):
        return "Hello %s" % name
    marie.expose('/', index)
    
    marie.run()
    
This example changes two lines, but makes a huge difference. The line::

    return "Hello %s" % name
    
may look a little odd if you aren't used to it. The ``%s`` is a placeholder for
the value of the variable ``name``. Whatever the value of ``name`` is will put
in place for ``%s``. So if the value of ``name`` is "Marie" the function will
return "Hello Marie".

Our function has also been given two new arguments: ``environ`` and ``name``.
The first is automatically provided by the framework and is all of the
information about the request. The second will contain the value of the first
URL argument. A URL argument is any part of the URL that comes after the actual
exposed function. In this example if we were to visit "http://localhost/Marie"
our first URL argument would be "Marie" and therefore the value of ``name``
wouldbe "Marie". Alternativly if you were to visit "http://localhost/" there would
be no URL arguments and the value of ``name`` would default to "World"

All this results in the ability to visit "http://localhost/" and recieve the
message "Hello World" or to visit "http://localhost/Your%20Name" and it will
respond with "Hello Your Name"

If you take this example a little farther we can do this: ::

    import marie
    
    def index(environ, name="World", greeting="Hello"):
        return "%s %s" % (greeting, name)
    marie.expose('/', index)
    
    marie.run()

Now if you visit "http://localhost/" you will see "Hello World". If you visit
"http://localhost/Marie" it will respond with "Hello Marie" and
"http://localhost/Marie/Howdy" will return "Howdy Marie". Finally if you are
naughty and visit "`http://localhost/<script>alert("test")</script>`" you will
be disapointed.

Now that you are done move on to the :doc:`manual </manual>` and learn about
all the things that you can do with Marie.