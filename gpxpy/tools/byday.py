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