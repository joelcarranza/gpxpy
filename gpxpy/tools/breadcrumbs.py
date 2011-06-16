#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.breadcrumbs

Construct waypoints from tracks, creating a waypoint along the track
at a specified interval

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import re
import datetime;
from gpxpy import *
import pytz
import re

def total_seconds(td):
  return td.seconds + td.days * 24 * 3600
  
def duration(s):
  m = re.match('(\d+)([dhms])',s)
  if m is not None:
    i = int(m.group(1))
    t = m.group(2)
    if t == 's':
      return i
    elif t== 'm':
      return i*60
    elif t== 'h':
      return i*60*60
    elif t== 'd':
      return i*24*60*60
  else:
    raise Exception("Invalid: "+s)
  return m
    
# 1m in meters
def main(files,tz,maxDist,maxTime):
    gpx = GPX()
    for f in files:
      gpx.load(f)
    pts = []
    d = 0
    for trk in gpx.tracks:
      for p in trk.points():
        if len(pts) == 0:
          pts.append(p)
          d = 0
        else:
          d += pts[-1].dist(p)
          if d > maxDist:
            pts.append(p)
            d = 0
          if total_seconds(p.time-pts[-1].time) > maxTime:
            pts.append(p)
            d = 0
            
    for p in pts:
      # TODO: format with timezone
      localts = p.time.astimezone(tz)
      p.name = localts.strftime('%Y-%m-%d %H:%M')
    gpx = GPX()
    gpx.waypoints.extend(pts)
    return gpx

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Trim GPX file to time')
  parser.add_argument('-i', metavar='file',nargs="+",type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  parser.add_argument('-tz', type=pytz.timezone,default=pytz.utc)
  parser.add_argument('-d', type=float,default=1609)
  parser.add_argument('-t', type=duration,default='1h')
  args = parser.parse_args()
  gpx = main(args.i,args.tz,args.d,args.t)
  gpx.write(args.o)