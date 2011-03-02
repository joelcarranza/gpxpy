#!/usr/bin/env python
# encoding: utf-8
"""
merge.py

Created by Joel Carranza on 2011-02-11.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import argparse
from GPX import *

def merge(files):
  gpx = GPX()
  for a in files:
    gpx.load(a)
    
  # sort waypoints by name
  gpx.waypoints.sort(key=lambda w:w.name or '')
  # sort routes by name
  gpx.routes.sort(key=lambda r:r.name or '')  
  
  # sort tracks by time
  # TODO: what if they don't have time?
  gpx.tracks.sort(key=lambda t:t[0][0].time)
  return gpx

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trim GPX file to time')
    parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
    parser.add_argument('-w', action='store_true')
    parser.add_argument('-t', action='store_true')
    parser.add_argument('-r', action='store_true')
    parser.add_argument('files', metavar='file',nargs="+",type=argparse.FileType('r'),default=sys.stdin)
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