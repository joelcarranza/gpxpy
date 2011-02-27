#!/usr/bin/env python
# encoding: utf-8
"""
trim.py

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import re
import datetime;
from GPX import *
from csv import DictReader

#bounds = (36.559065887999999, -119.559910528, 37.872216623, -118.291351572)

def main(files):
  gpx = GPX()
  
  for f in files:
    reader = DictReader(f)
    for row in reader:
        lat = float(row['PRIM_LAT_DEC'])
        lon = float(row['PRIM_LONG_DEC'])
        name = row['FEATURE_NAME']
        featClass = row['FEATURE_CLASS']
        gpx.newWaypoint(lat,lon,name=name,type=featClass,desc="""
        Ele: %(ELEV_IN_FT)sft
        Type: %(FEATURE_CLASS)s
        %(COUNTY_NAME)s, %(STATE_ALPHA)s
        """ % row)
  return gpx

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Trim GPX file to time')
  parser.add_argument('-i', metavar='file',nargs="+",type=argparse.FileType('rU'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  args = parser.parse_args()
  gpx = main(args.i)
  gpx.write(args.o)
