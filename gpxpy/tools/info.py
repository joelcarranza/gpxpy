#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.info

Created by Joel Carranza on 2011-06-15.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from gpxpy import GPX
import argparse

def fmt_ts(d):
  return d.strftime("%c")

def metadata(obj):
  if obj.name:
    print "Name: %s" % obj.name

def bounds(obj):
  # TODO: could geohash here
  print "Bounds: %.3f,%.3f  %.3f,%.3f" % obj.bounds()

def timespan(obj):
  # definately support  formatting in a specified timezone here!
  (starts,endts) = obj.timespan()
  
  print "Start: "+fmt_ts(starts)
  print "  End: "+fmt_ts(endts)

def point(p):
  print "%.3f,%.3f" % (p.lat,p.lon)
  
def gpx_info(gpx):
  metadata(gpx)
  bounds(gpx)
  timespan(gpx)

  if len(gpx.waypoints):
    print "%d waypoints" % len(gpx.waypoints)
  for w in gpx.waypoints:
    print "[wpt]: %s" % w.name
    
  if len(gpx.tracks):
    print "%d tracks" % len(gpx.tracks)
  for t in gpx.tracks:
    print "[trk]: %s" % t.name

  if len(gpx.routes):
    print "%d routes" % len(gpx.routes)
  for r in gpx.routes:
    print "[rte]: %s" % r.name
  
  
def waypoint_info(wpt):
  metadata(wpt)
  print "Lat: %.3f" % wpt.lat
  print "Lon: %.3f" % wpt.lon
  # TODO: geohash?
  if wpt.ele:
    print "Ele: %f" % wpt.ele
  if wpt.time:
    print "Time: %s" % fmt_ts(wpt.time)
  

def route_info(rte):
  metadata(rte)
  bounds(rte)
  timespan(rte)
  print "%d points " % len(rte)
  for p in rte:
    point(p)
  
def track_info(trk):
  metadata(trk)
  bounds(trk)
  timespan(trk)
  print "%d points " % len(list(trk.points()))
  print "%d segments " % len(trk)
  for seg in trk:
    print "-------"
    for p in seg:
      point(p)

def name_filter(name):
  # TODO: future wildcard support!
  return lambda x: x.name == name

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Summary info from GPX file')
  parser.add_argument('infile', metavar='file',
                    help='gpx file')
  parser.add_argument('name', metavar='name',
                    nargs="?",
                    help='gpx file')

  args = parser.parse_args()
  gpx = GPX()
  gpx.load(args.infile)
  if args.name:
    f = name_filter(args.name)
    for w in filter(f,gpx.waypoints):
      waypoint_info(w)
    for r in filter(f,gpx.routes):
      route_info(r)
    for t in filter(f,gpx.tracks):
      track_info(t)
  else:
    gpx_info(gpx)
  
  
