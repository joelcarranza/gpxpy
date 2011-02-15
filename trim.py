#!/usr/bin/env python
# encoding: utf-8
"""
trim.py

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import re
import datetime;
from GPX import *

help_message = '''
The help message goes here.
'''
import pytz
tz = pytz.utc

def parseInt(s):
  if s:
    return int(s)
  else:
    return None
    
def parseDate(s,begin=True):
  m = re.match('(\d+)-(\d+)-(\d+)(?:T(\d+):(\d+)(?::(\d+))?)?',s)
  if m:
    year,month,day,h,m,s = map(parseInt,m.groups())
    if h is None:
      h = 0 if begin else 23
    if m is None:
      m = 0 if begin else 59
    if s is None:
      s = 0 if begin else 59
    return datetime.datetime(year,month,day,h,m,s,0,tz)
  else:
    raise Exception("Invalid date: "+s)

def parseDateRange(range):
  p = range.split(',')
  if len(p) == 1:
    p = (p[0],p[0])
  return (parseDate(p[0],True),parseDate(p[1],False))
  
def trimSegment(seg,dateRange):
  pts = []
  for p in seg:
    t = p.time
    if t and dateRange[0] <= t and t <= dateRange[1]:
      pts.append(p)
  return Path(pts) if len(pts) > 0 else None

class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg


def main(argv=None):
  if argv is None:
    argv = sys.argv
  try:
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
      
    fn,dr = args
    dateRange = parseDateRange(dr)
    gpx = GPX()
    gpx.load(fn)
    
    for trk in gpx.tracks:
      s = map(lambda seg:trimSegment(seg,dateRange),trk)
      s = filter(lambda x: x is not None,s)
      print s

  
  except Usage, err:
    print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
    print >> sys.stderr, "\t for help use --help"
    return 2


if __name__ == "__main__":
  sys.exit(main())
