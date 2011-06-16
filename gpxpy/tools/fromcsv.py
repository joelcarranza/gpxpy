#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy.tools.fromcsv

Creates a GPX file from a CSV file

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import re
import datetime;
from gpxpy import *
import pytz
from csv import DictReader

def main(files,latField,lonField,nameField,typeField):
  # TODO: optionally turn into track or route
  gpx = GPX()
  for f in files:
    reader = DictReader(f)
    for row in reader:
        lat = float(row[latField])
        lon = float(row[lonField])
        w = gpx.newWaypoint(lat,lon)
        if nameField is not None:
          w.name = row[nameField]
        if typeField is not None:
          w.type = row[typeField]          
  return gpx

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Trim GPX file to time')
  parser.add_argument('-i', metavar='file',nargs="+",type=argparse.FileType('rU'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  args = parser.parse_args()
  # TODO: these must not be hard coded
  gpx = main(args.i,'PRIM_LAT_DEC','PRIM_LONG_DEC','FEATURE_NAME','FEATURE_CLASS')
  gpx.write(args.o)
