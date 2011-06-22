#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.byday

Split tracks into per-day components

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import re
import datetime;
from gpxpy import *
import pytz

# byday really should be split - support
# numerous options

def seconds(dur):
  return dur

def timediff(wpt0,wpt1):
  return seconds(wpt1.time - wpt0.time)
  
def dist(wp0,wpt1):
  return wp10.dist(wpt1)

def limit(func, max, wpt0, wpt1):
  return lambda wpt0,wpt1: func(wpt0,wpt1) < max
  
class Accumulator(object):
  def __init__(self,func,max):
    self.func = func
    self.max = max
    self.total = total
  
  def __call__(self,wpt0,wpt1):
    v = self.total + self.func(wp0,wp1)
    if v < self.max:
      self.total = v
      return True
    else:
      self.total = 0
      return False

def accumulate(func, max, wpt0, wpt1):
  return Accumulator(func,max)  

def split_dist(max_dist):
  return lambda a,b: limit(dist,max_dist,a,b)

def split_travel_dist(max_dist):
  return lambda a,b: accumulate(dist,max_dist,a,b)

def split_time(max_time):
  return lambda a,b: limit(timedif,seconds(max_time),a,b)

def split_travel_dist(max_time):
  return lambda a,b: accumulate(timediff,seconds(max_time),a,b)


def binByDay(pts,tz):
  days = {}
  for p in pts:
    t = p.time
    if t is not None:
      # TODO: itertools groupby?
      t = tz.normalize(t.astimezone(tz))
      key = (t.year,t.month,t.day)
      if key not in days:
        days[key] = []
      days[key].append(p)
  return days

def main(files,tz):
    gpx = GPX()
    for f in files:
      gpx.load(f)
    days = {}
    for trk in gpx.tracks:
      for s in trk:
        for p in s:
          t = p.time
          if t is not None:
            t = t.astimezone(tz)
            key = (t.year,t.month,t.day)
            if key not in days:
              days[key] = []
            days[key].append(p)

    gpx = GPX()
    for day,pts in days.items():
      t = gpx.newTrack(name="-".join(map(str,day)),points=pts)
    gpx.tracks.sort(key=lambda t:t.name)
    return gpx

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Trim GPX file to time')
  parser.add_argument('-i', metavar='file',nargs="+",type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  parser.add_argument('-tz', type=pytz.timezone,default=pytz.utc)
  args = parser.parse_args()
  gpx = main(args.i,args.tz)
  gpx.write(args.o)