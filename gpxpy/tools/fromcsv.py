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

def main(file,latField,lonField,nameField,typeField):
  # TODO: optionally turn into track or route
  gpx = GPX()
  reader = DictReader(file)
  for row in reader:
      lat = float(row[latField])
      lon = float(row[lonField])
      w = gpx.newWaypoint(lat,lon)
      if nameField is not None:
        w.name = row[nameField]
      if typeField is not None:
        w.type = row[typeField]          
  return gpx

def run():
  parser = argparse.ArgumentParser(description='Creates a GPX file from a CSV file')
  parser.add_argument('-i', metavar='file',type=argparse.FileType('rU'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  parser.add_argument('-lat',metavar="field",default="LAT")
  parser.add_argument('-lon',metavar="field",default="LON")
  parser.add_argument('-name',metavar="field")
  parser.add_argument('-type',metavar="field")
  
  args = parser.parse_args()
  gpx = main(args.i,args.lat,args.lon,args.name,args.type)
  gpx.write(args.o)
  
if __name__ == "__main__":
  run()
