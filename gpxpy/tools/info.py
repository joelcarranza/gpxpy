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
import pytz

tz = pytz.utc


def fmt_dt(d):
  d = tz.normalize(d.astimezone(tz))
  return d.strftime("%D %T")

def fmt_timespan(dur):
  if dur is not None:
    start = tz.normalize(dur[0].astimezone(tz))
    end = tz.normalize(dur[1].astimezone(tz))    
    return start.strftime("%D %H:%M")+"-"+end.strftime("%D %H:%M")
  else:
    return "-"

def fmt_dist(m):
  # TODO: metric
  if m > 3000:
    return "%ikm" % (m/1000)
  return "%im" % m 

def metadata(obj):
  if obj.name:
    print "Name: %s" % obj.name

def bounds(obj):
  # TODO: could geohash here
  print "Bounds: %.3f,%.3f  %.3f,%.3f" % obj.bounds()

def timespan(obj):
  # definately support  formatting in a specified timezone here!
  (starts,endts) = obj.timespan()
  
  print "Start: "+fmt_dt(starts)
  print "  End: "+fmt_dt(endts)

def point(p):
  parts = [];
  if p.ele is None:
    parts.append("%.3f,%.3f" % (p.lat,p.lon))
  else:
    parts.append("%.3f,%.3f,%i" % (p.lat,p.lon,p.ele))
  
  if p.time is not None:
    parts.append(fmt_dt(p.time))
  # TODO: alternate formats
  # - HMS
  # - Geohash!
  print "\t".join(parts)
  
def gpx_info(gpx):
  metadata(gpx)
  bounds(gpx)
  timespan(gpx)

  # TODO: format name with (unnamed) if name is None
  # additional info here t/s 
  if len(gpx.waypoints):
    print "%d waypoints" % len(gpx.waypoints)
  for w in gpx.waypoints:
    print "[wpt]: "+waypoint_line(w)
    
  if len(gpx.tracks):
    print "%d tracks" % len(gpx.tracks)
  for t in gpx.tracks:
    print "[trk]: "+track_line(t)
    
  if len(gpx.routes):
    print "%d routes" % len(gpx.routes)
  for r in gpx.routes:
    print "[rte]: "+route_line(r)
  
def waypoint_line(w):
  print "[wpt]: %s" % w.name
  
def waypoint_info(wpt):
  metadata(wpt)
  print "Lat: %.3f" % wpt.lat
  print "Lon: %.3f" % wpt.lon
  # TODO: geohash?
  if wpt.ele:
    print "Ele: %f" % wpt.ele
  if wpt.time:
    print "Time: %s" % fmt_ts(wpt.time)
  
def route_line(r):
  print "[rte]: %s" % r.name

def route_info(rte):
  metadata(rte)
  bounds(rte)
  timespan(rte)
  print "%d points " % len(rte)
  for p in rte:
    point(p)

def track_line(t):
  return "%s\t%s\t%s" % (t.name,fmt_timespan(t.timespan()),fmt_dist(t.length()))
    
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

def run():
  parser = argparse.ArgumentParser(description='Summary info from GPX file')
  parser.add_argument('infile', metavar='file',
                    help='gpx file')
  parser.add_argument('-tz', type=pytz.timezone,default=pytz.utc)
                    
  parser.add_argument('name', metavar='name',
                    nargs="?",
                    help='name of a waypoint/track/route')

  args = parser.parse_args()
  global tz
  tz = args.tz 
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
  
if __name__ == "__main__":
  run()
  
