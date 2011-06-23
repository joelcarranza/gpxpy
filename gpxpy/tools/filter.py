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
import gpxpy.tools

# TODO: this really needs support for selectively importing tracks/routes/waypoints
# filter to within a geometry

def parse_date(s,begin=True):
  # TODO should take dates that are output in info
  # need robust date parsing
  # http://www.logarithmic.net/pfh/blog/01162445830
  # or 
  # http://labix.org/python-dateutil#head-217af1251c3f91cb598ccf3240c6ab8abcb30151
  
  m = re.match('(\d+)-(\d+)-(\d+)(?:T(\d+):(\d+)(?::(\d+))?)?',s)
  if m:
    # TODO: lambda? instead of parseInt
    year,month,day,h,m,s = map(lambda s: int(s) if s else None,m.groups())
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

def parse_date_range(range,tz):
  p = range.split(',')
  if len(p) == 1:
    p = (p[0],p[0])
  return (parse_date(p[0],tz,True),parse_date(p[1],tz,False))

def filter_by_date(p,t0,t1):
  t = p.time
  if not t:
    return False
  if t0 and t < t0:
    return False
  if t1 and t > t1:
    return False
  return True

  
def run():
  parser = argparse.ArgumentParser(description='Modify a GPX file to keep only what you want',parents=[gpxpy.tools.inoutargs()])
  parser.add_argument('-tz', type=gpxpy.tools.parse_timezone, help="Timezone of trim dates")
  parser.add_argument('-from', dest='t0',metavar="datetime",type=partial(parse_date,begin=True),help="Start date. Of the form YYYY-MM-DD HH:MM")
  parser.add_argument('-to', dest='t1',metavar="datetime", type=partial(parse_date,begin=False),help="End date. Of the form YYYY-MM-DD HH:MM")
  args = parser.parse_args()

  # parse GPX file
  gpx = gpxpy.tools.gpxin(args)
  
  # time filter
  t0 = args.t0
  t1 = args.t1
  if t0 or t1:
    if args.tz is not None:
      t0 = t0.replace(tzinfo=args.tz) if t0 else None
      t1 = t1.replace(tzinfo=args.tz) if t1 else None
  gpx.filter(lambda p: filter_by_date(p,t0,t1))
  # TODO: check empty before write!  
  gpxpy.tools.gpxout(gpx,args)
  
if __name__ == "__main__":
  run()
