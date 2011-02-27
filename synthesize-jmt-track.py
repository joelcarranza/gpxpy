#!/usr/bin/env python
# encoding: utf-8
from GPX import *
"""
supplement.py

Created by Joel Carranza on 2011-02-12.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
from itertools import groupby
import pytz
from datetime import timedelta
from datetime import datetime

help_message = '''
The help message goes here.
'''

gpx = GPX()
gpx.load("data/JMT_gps_log_trimmed.gpx")
jmt = GPX()
jmt.load("data/JMT.gpx")

# reverse because they are in opposite order
jmtpts = list(jmt.tracks[0].points())[::-1]

tz = pytz.timezone('America/Los_Angeles')

def dayKey(w):
  t = w.time
  t = t.astimezone(tz)
  return (t.year,t.month,t.day)
  
def closestPt(pts,pt):
  i = min(xrange(len(pts)),key=lambda i:pts[i].dist(pt))
  d = pts[i].dist(pt)
  return (i,d)

def totalDistance(pts):
  d = 0
  for ix in xrange(1,len(pts)):
    d += pts[ix].dist(pts[ix-1])
  return d
  
def tinterp(t0,t1,u):
  #print u
  # 0 < u < 1
  delta = (t1-t0).seconds
  return t0+timedelta(seconds=u*delta)
  
def selectJmtPts(pts, start,finish):
  a,da = closestPt(pts,start)
  b,db = closestPt(pts,finish)
  if da > 200 or db > 200:
    return None
  if a == b:
    return None
  if b < a:
    a,b = (b,a)
  result = pts[a:b]
  if start.time and finish.time:
    totald = totalDistance(result) + result[0].dist(start)+result[-1].dist(finish)
    d = result[0].dist(start)
    for i in xrange(0,len(result)):
      if i:
        d += result[i].dist(result[i-1])
      result[i].time = tinterp(start.time,finish.time,d/totald)
    
  del pts[a:b]  
  return result

def ptime(str):
  t = datetime.strptime(str,"%Y-%m-%d %H:%M").replace(tzinfo=tz)
  print t
  return t

def createTrack(pts, start, finish):
  return Track(points=selectJmtPts(pts,start,finish))

gpxpts = list(gpx.allpoints())
gpx.waypoints.append(Waypoint(37.73,-119.559,time=ptime('2010-8-29 08:00')))
gpx.waypoints.append(Waypoint(37.7888,-119.434,time=ptime('2010-8-29 13:00')))
gpx.waypoints.append(Waypoint(37.7888,-119.434,time=ptime('2010-8-30 08:00')))
gpx.waypoints.append(Waypoint(37.841085,-119.286346,time=ptime('2010-8-30 13:00')))
gpx.waypoints.append(Waypoint(37.841085,-119.286346,time=ptime('2010-8-31 08:00')))
gpx.waypoints.append(Waypoint( 37.744712,-119.212257,time=ptime('2010-8-31 13:00')))
# additional fixed pts
gpx.waypoints.append(Waypoint(  37.609801,-119.075117,time=ptime('2010-9-2 14:11')))
gpx.waypoints.append(Waypoint(37.412684,-118.924876,time=ptime('2010-9-4 14:16')))
 
gpx.waypoints.append(Waypoint(37.412684,-118.924876,time=ptime('2010-9-5 9:39')))
gpx.waypoints.append(Waypoint(36.634764,-118.385863,time=ptime('2010-9-13 8:00')))
#gpxpts.extend(gpx.waypoints)
gpxpts.sort(key=lambda w:w.time)

gpx.tracks = []

for day,result in groupby(gpxpts,key=dayKey):
  pts = list(result)
  out = [pts[0]]
  for ix in xrange(1,len(pts)):
    pa = pts[ix-1]
    pb = pts[ix]
    dt = pb.time-pa.time
    if dt.seconds > 5*60 and pa.dist(pb) > 50:
      np = selectJmtPts(jmtpts,pts[ix-1],pts[ix])
      if np is not None:
        out.extend(np)
      else:
        print "selectJmtPts failed %s to %s" % (pa,pb)
        #gpx.newWaypoint(pa.lat,pa.lon,name="Failed! %s - %s" % (pa.time.astimezone(tz),pb.time.astimezone(tz)))
    out.append(pb)
  gpx.newTrack(points=out,name=str(day))
  

gpx.write("jmt-tracks.gpx")