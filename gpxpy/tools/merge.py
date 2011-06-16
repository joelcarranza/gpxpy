#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.merge

Merge several GPX tracks into one

Created by Joel Carranza on 2011-02-11.
"""

import argparse
from gpxpy import *
from datetime import datetime
import pytz

def merge(files):
  gpx = GPX()
  for a in files:
    gpx.load(a)
    
  # sort waypoints by name
  gpx.waypoints.sort(key=lambda w:w.name or '')
  # sort routes by name
  gpx.routes.sort(key=lambda r:r.name or '')  
  
  # sort tracks by time, then name
  # if there is no time for a particular track - use timezero!
  timezero = datetime(1,1,1,tzinfo=pytz.utc)
  gpx.tracks.sort(key=lambda t:(t[0][0].time or timezero,t.name))
  return gpx


def run():
    parser = argparse.ArgumentParser(description='Merge multiple gpx files into one')
    parser.add_argument('-o', metavar='out-file',type=argparse.FileType('w'),default=sys.stdout)
    parser.add_argument('-w', action='store_true',help="waypoints only")
    parser.add_argument('-t', action='store_true',help="tracks only")
    parser.add_argument('-r', action='store_true',help="routes only")
    parser.add_argument('files', metavar='file',nargs="+",type=argparse.FileType('r'),default=sys.stdin,help="output file")
    args = parser.parse_args()
    gpx = merge(args.files);
    if args.w or args.t or args.r:
      if not args.w:
        gpx.waypoint = []
      if not args.t:
        gpx.tracks = []
      if not args.r:
        gpx.route = []
    gpx.write(args.o)
    

if __name__ == "__main__":
  run()
