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
import argparse

help_message = '''
The help message goes here.
'''

parser = argparse.ArgumentParser(description='Trim GPX file to time')
parser.add_argument('-i', metavar='file',type=argparse.FileType('r'),default=sys.stdin)
parser.add_argument('-t', metavar='file',type=argparse.FileType('r'))
parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
args = parser.parse_args()

gpx = GPX()
gpx.load(args.i)
jmt = GPX()
jmt.load(args.t)

# reverse because they are in opposite order
jmtpts = list(jmt.tracks[0].points())[::-1]

tz = pytz.timezone('America/Los_Angeles')

def dayKey(w):
  t = w.time
  t = tz.normalize(t.astimezone(tz))
  return (t.year,t.month,t.day)
  
def closestPt(pts,pt):
  i = min(xrange(len(pts)),key=lambda i:pts[i].dist(pt))
  d = pts[i].dist(pt)
  return (i,d)
  
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
    totald = wptdistance(result) + result[0].dist(start)+result[-1].dist(finish)
    d = result[0].dist(start)
    for i in xrange(0,len(result)):
      if i:
        d += result[i].dist(result[i-1])
      result[i].time = tinterp(start.time,finish.time,d/totald)
    
  del pts[a:b]  
  return result

def ptime(str):
  return tz.localize(datetime.strptime(str,"%Y-%m-%d %H:%M"))

def createTrack(pts, start, finish):
  return Track(points=selectJmtPts(pts,start,finish))

gpxpts = [w for w in gpx.allpoints() if w.time is not None]
gpxpts.sort(key=lambda w:w.time)

gpx.tracks = []

for day,result in groupby(gpxpts,key=dayKey):
  print day
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
  gpx.newTrack(points=out,name="%d-%d-%d" % day)
  
gpx.write(args.o)