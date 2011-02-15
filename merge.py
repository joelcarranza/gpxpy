#!/usr/bin/env python
# encoding: utf-8
"""
merge.py

Created by Joel Carranza on 2011-02-11.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import StringIO
from GPX import *

# TODO: support loading only wpt/tracks/routes

help_message = '''
Merges two or more GPX files into a single file
'''

def merge(src,dest):
  dest.waypoints.extend(src.waypoints)
  dest.routes.extend(src.routes)
  dest.tracks.extend(src.tracks)

def write(gpx,file=None):
  if file:
    gpx.write(file)
  else:
    s = StringIO.StringIO()
    gpx.write(s)
    print s.getvalue()

class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg


def main(argv=None):
  if argv is None:
    argv = sys.argv
  try:
    output = None
    try:
      opts, args = getopt.getopt(argv[1:], "ho:v", ["help", "output="])
    except getopt.error, msg:
      raise Usage(msg)
    # option processing
    for option, value in opts:
      if option == "-v":
        verbose = True
      if option in ("-h", "--help"):
        raise Usage(help_message)
      if option in ("-o", "--output"):
        output = value
        
    dest = GPX()
    for a in args:
      src = GPX()
      src.load(a)
      merge(src,dest)
    write(dest,output)
  
  except Usage, err:
    print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
    print >> sys.stderr, "\t for help use --help"
    return 2


if __name__ == "__main__":
  sys.exit(main())
