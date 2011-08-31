#!/usr/bin/env python

from setuptools import setup, find_packages

sdict = {
    'name' : 'Marie',
    'version' : '1.0.5',
    'description' : 'A WSGI micro-framework for websites in Python',
    'long_description' : 'A WSGI micro-framework for websites in Python',
    'url': 'http://www.trydyingtolive.com/marie/',
    'author' : 'Mark W. Lee',
    'author_email' : 'trydyingtolive@gmail.com',
    'maintainer' : 'Mark W. Lee',
    'maintainer_email' : 'trydyingtolive@gmail.com',
    'keywords' : ['Marie', 'WSGI', 'micro', 'framework', 'Redis', 'Mako'],
    'license' : 'GPLv3',
    'py_modules': ['marie'],
    'classifiers' : [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}
    
setup(**sdict)
