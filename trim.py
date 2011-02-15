#!/usr/bin/env python
# encoding: utf-8
"""
trim.py

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import re
import datetime;
from GPX import *
import pytz

def parseInt(s):
  if s:
    return int(s)
  else:
    return None
    
def parseDate(s,tz,begin=True):
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
    return datetime.datetime(year,month,day,h,m,s,ms,tz)
  else:
    raise Exception("Invalid date: "+s)

def parseDateRange(range,tz):
  p = range.split(',')
  if len(p) == 1:
    p = (p[0],p[0])
  return (parseDate(p[0],tz,True),parseDate(p[1],tz,False))

def trimSegment(seg,dateRange):
  pts = []
  for p in seg:
    t = p.time
    if t and dateRange[0] <= t and t <= dateRange[1]:
      pts.append(p)
  return Path(pts) if len(pts) > 0 else None

def main(input,output,dateRangeStr,tz):
    dateRange = parseDateRange(dateRangeStr,tz)
    
    gpx = GPX()
    gpx.load(input)
    
    for trk in gpx.tracks:
      s = map(lambda seg:trimSegment(seg,dateRange),trk)
      s = filter(lambda x: x is not None,s)
    gpx.write(output)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Trim GPX file to time')
  parser.add_argument('-i', metavar='file',type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  parser.add_argument('-tz', type=pytz.timezone,default=pytz.utc)
  parser.add_argument('dateRange')
  args = parser.parse_args()
  main(args.i,args.o,args.dateRange,args.tz)