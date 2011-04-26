#!/usr/bin/env python

sdict = {
    'name' : 'Marie',
    'version' : '1.0',
    'description' : 'A WSGI micro-framework for websites in Python',
    'long_description' : 'A WSGI micro-framework for websites in Python',
    'url': 'http://www.trydyingtolive.com/marie/',
    'author' : 'Mark W. Lee',
    'author_email' : 'trydyingtolive@gmail.com',
    'maintainer' : 'Mark W. Lee',
    'maintainer_email' : 'trydyingtolive',
    'keywords' : ['Marie', 'WSGI', 'micro', 'framework', 'Redis', 'Mako'],
    'license' : 'GPLv3',
    'packages' : ['marie'],
    'classifiers' : [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
setup(**sdict)
