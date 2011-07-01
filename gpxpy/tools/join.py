#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.join

Join tracks together if they are close enough within time or space

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import gpxpy.tools

def run():
  parser = argparse.ArgumentParser(description='Join GPX tracks together',parents=[gpxpy.tools.inoutargs()])
  parser.add_argument('-t', metavar="duration",type=gpxpy.tools.parse_timedelta,help="Join segments only if points are within this time period")
  parser.add_argument('-d', metavar="dist",type=gpxpy.tools.parse_dist,help="Join segments only if points are within this distance")
  # TODO: option to explode individual segments into tracks + rename!
  parser.add_argument('-x', action='store_true',help="Convert segments into tracks")
  
  args = parser.parse_args()
  gpx = gpxpy.tools.gpxin(args)
  gpx.join(args.d,args.t)
  if args.x:
    gpx.segments_to_tracks()
  gpxpy.tools.gpxout(gpx,args)
  
if __name__ == "__main__":
  run()