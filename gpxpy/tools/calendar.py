#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.calendar

Split tracks into per-day components

TODO: write out as multiple files

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import re
from datetime import timedelta
from gpxpy import *
import pytz

def parse_timedelta(str):
  m = re.match(r"(\d+)([dhms])",str)
  if m:
    n = int(m.group(1))
    units = m.group(2)
    if units == 'd':
      return timedelta(days=n)
    if units == 'h':
      return timedelta(hours=n)
    if units == 'm':
      return timedelta(minutes=n)
    if units == 's':
      return timedelta(seconds=n)
  raise Exception("Failed to parse %s" %str)
  
def round_cal(td,tz,time):
  time = tz.normalize(time.astimezone(tz))
  if td.days > 0:
    return (time.year,time.month,time.day/td.days)
  else:
    s = (time.hour*3600+time.minute*60+time.second)/td.seconds
    return  (time.year,time.month,time.day,s)
  
def split_calendar(td,tz,wpt0,wpt1):
  return round_cal(td,tz,wpt0.time) == round_cal(td,tz,wpt1.time)

def split(gpx,dt,tz):
  gpx.join()
  for t in gpx.tracks:
    t.split(lambda wpt0,wpt1: split_calendar(dt,tz,wpt0,wpt1))
  segments = []
  for t in gpx.tracks:
    segments.extend(t)
  gpx.tracks = [Track(points=s) for s in segments]
  for t in gpx.tracks:
    t.name = t[0][0].time.strftime("%D" if dt.days > 0 else "%D %H:%M")
  return gpx

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Write GPX files according to time')
  parser.add_argument('-i', metavar='file',type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  parser.add_argument('-tz', type=pytz.timezone,default=pytz.utc)
  parser.add_argument('-t', type=parse_timedelta,default='1d')
  
  args = parser.parse_args()
  gpx = GPX()
  gpx.load(args.i)
  gpx = split(gpx,args.t,args.tz)
  gpx.write(args.o)