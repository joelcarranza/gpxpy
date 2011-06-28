#!/usr/bin/env python
from distribute_setup import use_setuptools
use_setuptools()
from distutils.core import setup

setup(name='gpxpy',
      version='0.1',
      description='GPX library',
      author='Joel Carranza',
      author_email='joel.carranza@gmail.com',
      url='http://carranza-collective.com/joel/',
      test_suite='gpxpy.test',
      packages=['gpxpy', 'gpxpy.tools'],
      scripts=['scripts/gpxinfo','scripts/gpxmerge','scripts/gpx2kml','scripts/gpxfilter','scripts/gpxsplit','scripts/gpxcalendar']
     )