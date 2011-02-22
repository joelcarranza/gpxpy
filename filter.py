#!/usr/bin/env python
# encoding: utf-8
"""
filter.py

Modify an existing GPX file to include only the portions you desire. 
Includes keeping only tracks/routes/waypoints, a specific time period
or a specific location.

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 Joel Carranza. All rights reserved.
"""

import sys
import argparse
import re
import datetime
import GPX
import pytz
from functools import partial

# TODO: this really needs support for selectively importing tracks/routes/waypoints
# filter to within a geometry
# probably could be renamed filter too :)

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
    ms = s = 0 if begin else 59 # ms must be between 1..60 ??
    return datetime.datetime(year,month,day,h,m,s,ms,pytz.utc)
  else:
    raise Exception("Invalid date: "+s)

def parseDateRange(range,tz):
  p = range.split(',')
  if len(p) == 1:
    p = (p[0],p[0])
  return (parseDate(p[0],tz,True),parseDate(p[1],tz,False))

def filterByDate(gpx,t0,t1):
    def filter(p):
      t = p.time
      if not t:
        return False
      if t0 and t < t0:
        return False
      if t1 and t > t1:
        return False
      return True
    gpx.filter(filter)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Modify GPX to keep only what you want')
  parser.add_argument('-i', metavar='file',type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  parser.add_argument('-tz', type=pytz.timezone)
  parser.add_argument('-from', type=partial(parseDate,begin=True))
  parser.add_argument('-to', type=partial(parseDate,begin=False))
  args = parser.parse_args()
  # parse GPX file
  gpx = GPX.parse(args.i)
  
  # time filter
  t0 = getattr(args,'from')
  t1 = args.to
  if args.tz is not None:
    t0 = t0.replace(tzinfo=args.tz) if t0 else None
    t1 = t1.replace(tzinfo=args.tz) if t1 else None
  if t0 or t1:
    filterByDate(gpx,t0,t1)
    
  # write it out!
  gpx.write(args.o)