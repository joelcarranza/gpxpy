#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.filter

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
from gpxpy import *
import pytz
from functools import partial

# TODO: this really needs support for selectively importing tracks/routes/waypoints
# filter to within a geometry

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
  parser = argparse.ArgumentParser(description='Modify a GPX file to keep only what you want')
  parser.add_argument('-i', dest='infile',metavar='file',type=argparse.FileType('r'),default=sys.stdin,help="GPX file to process. If none is specified STDIN will be use")
  parser.add_argument('-o', dest='outfile',metavar='file',type=argparse.FileType('w'),default=sys.stdout,help="file location for output. If none is specified STDOUT will be use")
  parser.add_argument('-tz', type=pytz.timezone, help="Timezone of trim dates")
  parser.add_argument('-from', dest='t0',metavar="datetime",type=partial(parseDate,begin=True),help="Start date. Of the form YYYY-MM-DD HH:MM")
  parser.add_argument('-to', dest='t1',metavar="datetime", type=partial(parseDate,begin=False),help="End date. Of the form YYYY-MM-DD HH:MM")
  parser.add_argument('--gpx-name', dest='gpxname',metavar="name", help="Name for resulting GPX file")
  parser.add_argument('--gpx-description', dest='gpxdesc',metavar="name", help="Description for resulting GPX file")
  args = parser.parse_args()
  # parse GPX file
  gpx = parse(args.infile)
  
  # time filter
  t0 = args.t0
  t1 = args.t1
  if t0 or t1:
    if args.tz is not None:
      t0 = t0.replace(tzinfo=args.tz) if t0 else None
      t1 = t1.replace(tzinfo=args.tz) if t1 else None
    filterByDate(gpx,t0,t1)
    
  # write it out!
  if args.gpxname is not None:
    gpx.name = args.gpxname
  if args.gpxdesc is not None:
    gpx.desc = args.gpxdesc
  gpx.write(args.outfile)