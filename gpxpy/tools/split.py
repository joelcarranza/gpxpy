#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.split

Split tracks into per-day components

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import re
from datetime import timedelta
from gpxpy import *
import pytz
import gpxpy.tools

  
class DistanceSplitter(object):
  def __init__(self,max_dist):
    self.max_dist = max_dist
    self.total = 0
  
  def __call__(self,wpt0,wpt1):
    v = self.total + wpt0.dist(wpt1)
    if v < self.max_dist:
      self.total = v
      return True
    else:
      self.total = 0
      return False

class TimeSplitter(object):
  def __init__(self,max_duration):
    self.max_dur = max_duration
    self.total = timedelta()

  def __call__(self,wpt0,wpt1):
    v = self.total + (wpt1.time-wpt0.time)
    if v < self.max_dur:
      self.total = v
      return True
    else:
      self.total = timedelta()
      return False

def split(gpx,dist,dt):
  gpx.join()
  if dist is not None:
    for t in gpx.tracks:
      t.split(DistanceSplitter(dist))
  if dt is not None:
    for t in gpx.tracks:
      t.split(TimeSplitter(dt))
  segments = []
  for t in gpx.tracks:
    segments.extend(t)
  gpx.tracks = [Track(points=s) for s in segments]
  for t in gpx.tracks:
    t.name = str(t[0][0].time)
  return gpx

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Split GPX file according to time or distance',parents=[gpxpy.tools.inoutargs()])
  parser.add_argument('-t', type=gpxpy.tools.parse_timedelta)
  parser.add_argument('-d', type=gpxpy.tools.parse_dist)
  
  args = parser.parse_args()
  gpx = gpxpy.tools.gpxin(args)
  gpx = split(gpx,args.d,args.t)
  gpxpy.tools.gpxout(gpx,args)