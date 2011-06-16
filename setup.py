#!/usr/bin/env python

from distutils.core import setup

setup(name='gpxpy',
      version='0.1',
      description='GPX library',
      author='Joel Carranza',
      author_email='joel.carranza@gmail.com',
      url='http://carranza-collective.com/joel/',
      packages=['gpxpy', 'gpxpy.tools'],
      scripts=['scripts/gpxinfo']
     )