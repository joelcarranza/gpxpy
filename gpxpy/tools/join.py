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
  # TODO: option to explode individual segments into tracks + rename!
  parser = argparse.ArgumentParser(description='Join GPX tracks together',parents=[gpxpy.tools.inoutargs()])
  # TODO: explain possible formats here
  parser.add_argument('-t', metavar="duration",type=gpxpy.tools.parse_timedelta,help="Join segments only if points are within this time period")
  parser.add_argument('-d', metavar="dist",type=gpxpy.tools.parse_dist,help="Join segments only if points are within this distance")
  
  args = parser.parse_args()
  gpx = gpxpy.tools.gpxin(args)
  gpx.join(args.d,args.t)
  gpxpy.tools.gpxout(gpx,args)
  
if __name__ == "__main__":
  run()