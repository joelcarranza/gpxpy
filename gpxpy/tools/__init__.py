import argparse
import sys
import gpxpy
from datetime import timedelta
import pytz
import re

def inoutargs():
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('-i', metavar='file',type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  return parser
  
def gpxin(args):
  return gpxpy.parse(args.i)
  
def gpxout(gpx,args):
  gpx.write(args.o)
  
units_conv = dict(m=1.0,mi=1609.344,ft=0.3048,km=1000)

def parse_dist(str):
  m = re.match(r"(\d+(?:\.\d+)?)([a-zA-Z]+)?",str)
  if m:
    n = float(m.group(1))
    units = (m.group(2) or "m").lower()
    return n*units_conv[units]
  raise Exception("Failed to parse %s" %str)

def parse_timezone(str):
  return pytz.timezone(str)

def parse_timedelta(str):
  m = re.match(r"(\d+)([dhms])",str)
  if m:
    n = int(m.group(1))
    units = m.group(2)
    if units == 'd':
      return timedelta(days=n)
    if units == 'h':
      return timedelta(hours=n)
    if units == 'm':
      return timedelta(minutes=n)
    if units == 's':
      return timedelta(seconds=n)
  raise Exception("Failed to parse %s" %str)